import json
import os
from typing import Any, Optional


def _allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]


def cors_headers(origin: Optional[str] = None) -> dict[str, str]:
    allowed = _allowed_origins()
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Credentials": "true",
    }
    if origin and origin in allowed:
        headers["Access-Control-Allow-Origin"] = origin
    elif len(allowed) == 1:
        headers["Access-Control-Allow-Origin"] = allowed[0]
    return headers


def api_response(
    status_code: int,
    body: Any,
    event: Optional[dict] = None,
    headers: Optional[dict[str, str]] = None,
) -> dict:
    origin = None
    if event:
        origin = (event.get("headers") or {}).get("origin") or (event.get("headers") or {}).get(
            "Origin"
        )
    base = cors_headers(origin)
    if headers:
        base.update(headers)
    return {
        "statusCode": status_code,
        "headers": base,
        "body": json.dumps(body, default=str),
    }


def error_response(message: str, status_code: int = 400, event: Optional[dict] = None) -> dict:
    return api_response(status_code, {"error": message}, event=event)
