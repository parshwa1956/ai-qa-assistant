import json
from typing import Any, Callable


def parse_body(event: dict) -> dict[str, Any]:
    body = event.get("body")
    if not body:
        return {}
    if event.get("isBase64Encoded"):
        import base64

        body = base64.b64decode(body).decode("utf-8")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body


def route_key(event: dict) -> str:
    return event.get("routeKey") or event.get("rawPath", "")


def path_param(event: dict, name: str) -> str | None:
    return (event.get("pathParameters") or {}).get(name)


def query_param(event: dict, name: str, default: str | None = None) -> str | None:
    return (event.get("queryStringParameters") or {}).get(name, default)
