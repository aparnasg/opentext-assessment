"""Fetch OpenText HTML and convert article content to Markdown without an AI model."""
import hashlib
import json
import re
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup, NavigableString
from markdownify import markdownify

MAX_BYTES = 2_000_000
URL = re.compile(r"https://my\.opentext\.com/support/article/(?:[a-z0-9]+(?:-[a-z0-9]+)*/)?([0-9]{1,12})/?\Z")


class ArticleError(Exception):
    pass


def article_id(url: str) -> str:
    """Accept only the supported HTTPS host/article path and return its numeric ID."""
    match = URL.fullmatch(url)
    if not match:
        raise ValueError("Use an HTTPS my.opentext.com/support/article/<numeric-id> URL")
    return match[1]


def embedded_article(soup: BeautifulSoup, ident: str):
    """Read only the matching Nuxt article record; never execute page scripts.

    Nuxt stores objects in a flat JSON array and uses integer references.
    Resolve only the three fields needed here, rather than arbitrary graphs.
    """
    script = soup.find("script", id="__NUXT_DATA__", type="application/json")
    if script is None:
        return None
    try:
        data = json.loads(script.string or "")
        if not isinstance(data, list):
            return None

        def resolve(index):
            if type(index) is not int or not 0 <= index < len(data):
                raise ValueError("Invalid article reference")
            return data[index]

        for record in data:
            if not isinstance(record, dict) or f"support-article-{ident}" not in record:
                continue
            article = resolve(record[f"support-article-{ident}"])
            if not isinstance(article, dict):
                continue
            source_id, title, content = (resolve(article.get(key)) for key in ("Id", "Title", "Content"))
            if str(source_id) != ident or not isinstance(title, str) or not isinstance(content, str):
                continue
            fragment = BeautifulSoup("<article></article>", "html.parser")
            heading = fragment.new_tag("h1")
            heading.string = title
            fragment.article.append(heading)
            fragment.article.append(BeautifulSoup(content, "html.parser"))
            return fragment.article
    except (ValueError, TypeError, RecursionError):
        return None
    return None


def normalize_emphasis(body):
    """Simplify rich-text emphasis before Markdown generation; leave code intact."""
    for tag in list(body.find_all(["b", "strong", "i", "em"])):
        if tag.find_parent(["pre", "code"]):
            continue
        family = ["b", "strong"] if tag.name in {"b", "strong"} else ["i", "em"]
        if tag.find_parent(family) or tag.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"]):
            tag.unwrap()
        else:
            tag.name = "strong" if family[0] == "b" else "em"
    # Adjacent spans of the same emphasis need one pair of Markdown markers.
    for tag in list(body.find_all(["strong", "em"])):
        if tag.parent is None or tag.find_parent(["pre", "code"]):
            continue
        while True:
            sibling = tag.next_sibling
            gap = None
            if isinstance(sibling, NavigableString) and not sibling.strip():
                gap, sibling = sibling, sibling.next_sibling
            if getattr(sibling, "name", None) != tag.name:
                break
            if gap is not None:
                tag.append(gap.extract())
            for child in list(sibling.contents):
                tag.append(child.extract())
            sibling.decompose()


def convert(html: str, url: str) -> dict:
    """Convert supplied HTML into Markdown and source metadata without network calls."""
    ident = article_id(url)
    soup = BeautifulSoup(html, "html.parser")
    # Conservative selectors: never convert the entire navigation/login shell.
    body = soup.select_one('[itemprop="articleBody"], .knowledge-article-content, article')
    if body is None:
        body = embedded_article(soup, ident)
    if body is None:
        raise ArticleError("Article body unavailable. Supply an authorized HTML export containing <article>.")
    for tag in body.select("script, style, nav, footer, form, iframe, button"):
        tag.decompose()
    heading = body.find("h1")
    title = heading.get_text(" ", strip=True) if heading else (soup.title.get_text(" ", strip=True) if soup.title else f"Article {ident}")
    if heading:
        # The title is added once in the Markdown header below.
        heading.decompose()
    if len(body.get_text(" ", strip=True)) < 40 or body.get_text(" ", strip=True).lower() in {"loading article...", "sign in"}:
        raise ArticleError("Article body is empty or is an access/loading placeholder")
    # Join relative resources against the source URL; drop unsafe schemes.
    for tag in body.find_all(["a", "img"]):
        attr = "href" if tag.name == "a" else "src"
        target = urljoin(url, tag.get(attr, ""))
        if urlsplit(target).scheme in {"https", "http", "mailto"} and not (tag.name == "img" and urlsplit(target).scheme == "mailto"):
            tag[attr] = target
        else:
            tag.attrs.pop(attr, None)
    normalize_emphasis(body)
    text = markdownify(str(body), heading_style="ATX", bullets="-").strip()
    markdown = f"# {title}\n\nSource: {url}\n\n{text}\n"
    # The API uses this stable content hash to construct its ETag.
    return {"id": ident, "title": title, "source_url": url, "markdown": markdown,
            "sha256": hashlib.sha256(markdown.encode()).hexdigest()}


async def fetch(url: str) -> str:
    """Retrieve HTML with bounded reads and explicitly validated redirects."""
    ident = article_id(url)
    # Observed OpenText route behavior: /article/<id> serves a generic shell
    # to plain HTTP clients; /article/<text>/<id> includes the article JSON.
    # The server resolves by ID even with the neutral text segment "knowledge".
    # Keep explicit slug URLs unchanged. This upstream convention needs monitoring.
    if urlsplit(url).path.rstrip("/") == f"/support/article/{ident}":
        url = f"https://my.opentext.com/support/article/knowledge/{ident}"
    # Redirects must stay on the same HTTPS host, article route and article ID.
    async with httpx.AsyncClient(timeout=httpx.Timeout(15, connect=5), follow_redirects=False, trust_env=False) as client:
        for attempt in range(4):
            async with client.stream("GET", url, headers={"User-Agent": "KnowledgeMarkdownAssessment/1.0", "Accept": "text/html"}) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    target = urljoin(url, response.headers.get("location", ""))
                    try:
                        valid = bool(response.headers.get("location")) and article_id(target) == ident
                    except ValueError:
                        valid = False
                    if not valid or attempt == 3:
                        raise ArticleError("Unsafe or excessive source redirects")
                    url = target
                    continue
                if response.status_code != 200:
                    raise ArticleError(f"Source returned HTTP {response.status_code}")
                if "text/html" not in response.headers.get("content-type", "").lower():
                    raise ArticleError("Source did not return HTML")
                chunks, size = [], 0
                # Enforce the size limit while streaming, not after a full download.
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ArticleError("Source exceeds the 2 MB limit")
                    chunks.append(chunk)
                return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
