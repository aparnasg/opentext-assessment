import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.converter import ArticleError, article_id, convert, fetch
from app.triangle import triangle, triangle_mn

URL = "https://my.opentext.com/support/article/2341059"
HTML = '''<html><title>Fallback</title><nav>Ignore me</nav><article><h1>Recovery guide</h1>
<p>Follow these steps to restore the service safely after an unexpected interruption.</p>
<h2>Resolution</h2><ol><li>Stop service</li><li>Restore backup</li></ol>
<pre><code>restart --safe</code></pre><a href="/support/article/1986936">Related</a>
<a href="javascript:alert(1)">Unsafe</a><script>secret()</script>
<table><tr><th>Code</th><th>Meaning</th></tr><tr><td>200</td><td>OK</td></tr></table></article></html>'''
client = TestClient(main.app)


def test_triangle():
    assert triangle() == "*\n***\n****"


@pytest.mark.parametrize("m,n,expected", [
    (1, 4, "****"),
    (4, 1, "*\n*\n*\n*"),
    (1, 1, "*"),
    (3, 4, "*\n***\n****"),
    (5, 8, "*\n***\n*****\n*******\n********"),
])
def test_bonus_triangle(m, n, expected):
    assert triangle_mn(m, n) == expected


@pytest.mark.parametrize("m,n", [(0, 2), (2, -1), (True, 2), (2, False), (2.1, 4), ("3", 4)])
def test_bonus_triangle_rejects_invalid_dimensions(m, n):
    with pytest.raises(ValueError):
        triangle_mn(m, n)


@pytest.mark.parametrize("url", ["http://my.opentext.com/support/article/1", "https://evil.test/1", "https://my.opentext.com.evil.test/support/article/1", URL + "?x=1", URL + "/../2"])
def test_reject_urls(url):
    with pytest.raises(ValueError):
        article_id(url)


def test_conversion():
    result = convert(HTML, URL)
    text = result["markdown"]
    assert text.startswith("# Recovery guide\n")
    assert "## Resolution" in text and "restart --safe" in text
    assert "https://my.opentext.com/support/article/1986936" in text
    assert "| Code" in text
    assert all(x not in text for x in ["Ignore me", "secret()", "javascript:"])
    assert result == convert(HTML, URL)


@pytest.mark.parametrize("fragment,expected", [
    ('<em><strong><strong>Note</strong>:</strong></em>', '***Note:***'),
    ('<strong>(Last update:</strong><strong> 27th October 2026)</strong>', '**(Last update: 27th October 2026)**'),
    ('<b>First</b> <strong>second</strong>', '**First second**'),
    ('<h2><strong>Environment</strong></h2>', '## Environment'),
    ('<p><strong>Bold</strong> and <em>italic</em></p>', '**Bold** and *italic*'),
    ('<pre><code>value = "*****"</code></pre>', 'value = "*****"'),
])
def test_clean_emphasis_preserves_content(fragment, expected):
    page = '<article><h1>Formatting guide</h1><p>This paragraph supplies sufficient context for the article conversion.</p>' + fragment + '</article>'
    text = convert(page, URL)["markdown"]
    assert expected in text
    assert 'This paragraph supplies sufficient context' in text


@pytest.mark.parametrize("html", ["<main>Loading article...</main>", "<article>Loading article...</article>", "<form>Sign in</form>"])
def test_access_shells(html):
    with pytest.raises(ArticleError):
        convert(html, URL)


def test_api_cache_and_errors(monkeypatch):
    async def fixture(url):
        return HTML
    monkeypatch.setattr(main, "fetch", fixture)
    response = client.get("/api/articles/2341059")
    assert response.status_code == 200
    assert "s-maxage=300" in response.headers["cache-control"]
    assert client.get("/api/articles/2341059", headers={"If-None-Match": response.headers["etag"]}).status_code == 304
    assert client.get("/api/articles/invalid").status_code == 422
    async def blocked(url):
        raise ArticleError("login")
    monkeypatch.setattr(main, "fetch", blocked)
    response = client.get("/api/articles/2341059")
    assert response.status_code == 502 and response.headers["cache-control"] == "no-store"


def test_private_import(monkeypatch):
    monkeypatch.setenv("IMPORT_API_KEY", "test-only-key")
    payload = {"source_url": URL, "html": HTML}
    assert client.post("/api/convert", json=payload).status_code == 401
    response = client.post("/api/convert", json=payload, headers={"X-API-Key": "test-only-key"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/health").json() == {"status": "ok"}
    assert "textarea" in client.get("/").text


@pytest.mark.parametrize("status,content_type,body", [(302, "text/html", b"redirect"), (403, "text/html", b"login"), (200, "application/json", b"{}"), (200, "text/html", b"x" * 2_000_001)], ids=["redirect", "forbidden", "wrong-type", "oversized"])
def test_fetch_boundary(monkeypatch, status, content_type, body):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(lambda request: httpx.Response(status, headers={"content-type": content_type}, content=body))
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    with pytest.raises(ArticleError):
        asyncio.run(fetch(URL))


def test_embedded_nuxt_article():
    payload = [{"support-article-2341059": 1}, {"Id": 2, "Title": 3, "Content": 4}, "2341059", "Embedded guide", "<h2>Resolution</h2><p>Restore backup carefully and verify that the service is running correctly.</p>"]
    page = '<main>Loading article...</main><script id="__NUXT_DATA__" type="application/json">' + json.dumps(payload) + '</script>'
    result = convert(page, URL)
    assert result["title"] == "Embedded guide"
    assert "Restore backup" in result["markdown"]
    payload[2] = "1986936"
    with pytest.raises(ArticleError):
        convert('<script id="__NUXT_DATA__" type="application/json">' + json.dumps(payload) + '</script>', URL)


@pytest.mark.parametrize("payload", ["{broken", "{}", '[{"support-article-2341059":999}]', '[{"support-article-2341059":true}]'])
def test_bad_embedded_data(payload):
    with pytest.raises(ArticleError):
        convert('<script id="__NUXT_DATA__" type="application/json">' + payload + '</script>', URL)


@pytest.mark.parametrize("target", ["/support/article/example-title/2341059", "https://evil.test/support/article/2341059", "/support/article/1986936", "/login", "http://my.opentext.com/support/article/2341059"])
def test_redirect_validation(monkeypatch, target):
    original = httpx.AsyncClient
    calls = []
    def respond(request):
        calls.append(str(request.url))
        if len(calls) == 1:
            return httpx.Response(302, headers={"location": target})
        return httpx.Response(200, headers={"content-type": "text/html"}, text=HTML)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs))
    if target == "/support/article/example-title/2341059":
        assert asyncio.run(fetch(URL)) == HTML
        assert len(calls) == 2
        assert calls[0] == "https://my.opentext.com/support/article/knowledge/2341059"
    else:
        with pytest.raises(ArticleError):
            asyncio.run(fetch(URL))
        assert len(calls) == 1
