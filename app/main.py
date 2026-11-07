import asyncio
import hmac
import os
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from mangum import Mangum
from pydantic import BaseModel, Field

from .converter import ArticleError, MAX_BYTES, article_id, convert, fetch

app = FastAPI(title="OpenText Knowledge Markdown", version="1.0.0", docs_url=None, redoc_url=None)


class Export(BaseModel):
    source_url: str = Field(max_length=200)
    html: str = Field(min_length=1, max_length=MAX_BYTES)


@app.middleware("http")
async def security(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    return Path(__file__).with_name("index.html").read_text(encoding="utf-8")


@app.get("/ui.js")
def javascript():
    return Response(Path(__file__).with_name("ui.js").read_text(encoding="utf-8"), media_type="text/javascript")


@app.get("/api/articles/{ident}")
async def article(ident: str, request: Request):
    url = f"https://my.opentext.com/support/article/{ident}"
    try:
        article_id(url)
        html = await asyncio.wait_for(fetch(url), timeout=20)
        result = convert(html, url)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (ArticleError, httpx.HTTPError, TimeoutError) as exc:
        raise HTTPException(502, "Article unavailable; it may require login, JavaScript, or an authorized export.") from exc
    etag = '"' + result["sha256"] + '"'
    headers = {"ETag": etag, "Cache-Control": "public, max-age=60, s-maxage=300"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return JSONResponse(result, headers=headers)


@app.post("/api/convert")
async def exported_article(data: Export, x_api_key: Annotated[str | None, Header()] = None):
    key = os.getenv("IMPORT_API_KEY")
    if not key or not hmac.compare_digest(x_api_key or "", key):
        raise HTTPException(401, "Authorized export conversion requires an API key")
    if len(data.html.encode()) > MAX_BYTES:
        raise HTTPException(413, "HTML exceeds the 2 MB limit")
    try:
        return convert(data.html, data.source_url)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except ArticleError as exc:
        raise HTTPException(422, str(exc)) from exc


handler = Mangum(app, lifespan="off")
