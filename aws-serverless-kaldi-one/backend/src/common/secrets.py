import json
import os
from functools import lru_cache

import boto3

_openai_key_cache: str | None = None


@lru_cache(maxsize=1)
def get_openai_api_key() -> str:
    global _openai_key_cache
    if _openai_key_cache:
        return _openai_key_cache

    secret_arn = os.environ.get("OPENAI_SECRET_ARN", "").strip()
    param_name = os.environ.get("OPENAI_PARAMETER_NAME", "").strip()

    if secret_arn:
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_arn)
        raw = resp.get("SecretString", "")
        try:
            parsed = json.loads(raw)
            _openai_key_cache = parsed.get("OPENAI_API_KEY") or parsed.get("api_key") or raw
        except json.JSONDecodeError:
            _openai_key_cache = raw
    elif param_name:
        client = boto3.client("ssm")
        resp = client.get_parameter(Name=param_name, WithDecryption=True)
        _openai_key_cache = resp["Parameter"]["Value"]
    else:
        _openai_key_cache = os.environ.get("OPENAI_API_KEY", "")

    if not _openai_key_cache:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return _openai_key_cache
