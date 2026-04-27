import base64
import os
import mimetypes
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.abspath(__file__))

TEXT_TYPES = {
    ".html", ".css", ".js", ".json", ".txt", ".svg", ".xml", ".map"
}

CACHE_BY_EXT = {
    ".html": "no-cache",
    ".css":  "public, max-age=86400",
    ".js":   "public, max-age=86400",
    ".svg":  "public, max-age=86400",
    ".jpg":  "public, max-age=604800, immutable",
    ".jpeg": "public, max-age=604800, immutable",
    ".png":  "public, max-age=604800, immutable",
    ".ico":  "public, max-age=604800, immutable",
    ".woff": "public, max-age=604800, immutable",
    ".woff2":"public, max-age=604800, immutable",
}

mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/javascript", ".js")


def _resolve(path):
    """Map URL path to a safe file path inside ROOT. Returns None if traversal attempted."""
    p = unquote(path or "/").split("?", 1)[0]
    if p in ("", "/"):
        p = "/index.html"
    # extensionless pretty URLs → .html
    root, ext = os.path.splitext(p)
    if not ext:
        p = root + ".html"
    rel = p.lstrip("/")
    full = os.path.normpath(os.path.join(ROOT, rel))
    if not full.startswith(ROOT):
        return None
    return full


def _content_type(ext):
    mt, _ = mimetypes.guess_type("x" + ext)
    if mt:
        if ext in TEXT_TYPES and "charset" not in mt:
            return mt + "; charset=utf-8"
        return mt
    return "application/octet-stream"


def _request_path(event):
    # Lambda Function URL v2
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}
    if http.get("path"):
        return http["path"]
    # API Gateway / older shapes
    return event.get("rawPath") or event.get("path") or "/"


def lambda_handler(event, context):
    try:
        path = _request_path(event)
        full = _resolve(path)
        if full is None or not os.path.isfile(full):
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/html; charset=utf-8"},
                "body": "<h1>404</h1><p>Lost in transmission. <a href='/'>Return</a>.</p>",
            }

        ext = os.path.splitext(full)[1].lower()
        ctype = _content_type(ext)
        cache = CACHE_BY_EXT.get(ext, "public, max-age=3600")

        if ext in TEXT_TYPES:
            with open(full, "r", encoding="utf-8") as f:
                body = f.read()
            return {
                "statusCode": 200,
                "headers": {"Content-Type": ctype, "Cache-Control": cache},
                "body": body,
            }
        else:
            with open(full, "rb") as f:
                body = base64.b64encode(f.read()).decode("ascii")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": ctype, "Cache-Control": cache},
                "body": body,
                "isBase64Encoded": True,
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain; charset=utf-8"},
            "body": f"Internal Server Error: {e}",
        }
