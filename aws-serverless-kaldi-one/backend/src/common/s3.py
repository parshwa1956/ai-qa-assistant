import os
from typing import Optional

import boto3

UPLOADS_BUCKET = os.environ.get("UPLOADS_BUCKET", "")
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", "10485760"))
_s3 = boto3.client("s3")

ALLOWED_MIME = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/msword",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/json",
    "text/x-python",
    "text/javascript",
    "application/javascript",
}


def user_prefix(user_id: str) -> str:
    return f"{user_id}/"


def build_object_key(user_id: str, project_id: str, filename: str) -> str:
    from datetime import datetime, timezone

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    safe_name = filename.replace("/", "_").replace("\\", "_")[:200]
    return f"{user_id}/{project_id}/{ts}_{safe_name}"


def presign_upload(user_id: str, project_id: str, filename: str, content_type: str) -> dict:
    if content_type not in ALLOWED_MIME:
        raise ValueError(f"Unsupported content type: {content_type}")
    key = build_object_key(user_id, project_id, filename)
    url = _s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": UPLOADS_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=900,
        HttpMethod="PUT",
    )
    return {"uploadUrl": url, "objectKey": key, "bucket": UPLOADS_BUCKET}


def presign_download(object_key: str, user_id: str) -> str:
    if not object_key.startswith(user_prefix(user_id)):
        raise PermissionError("Access denied to object")
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": UPLOADS_BUCKET, "Key": object_key},
        ExpiresIn=3600,
    )


def get_object_bytes(object_key: str, user_id: str, max_bytes: Optional[int] = None) -> bytes:
    if not object_key.startswith(user_prefix(user_id)):
        raise PermissionError("Access denied to object")
    limit = max_bytes or MAX_UPLOAD_BYTES
    head = _s3.head_object(Bucket=UPLOADS_BUCKET, Key=object_key)
    size = head.get("ContentLength", 0)
    if size > limit:
        raise ValueError(f"File exceeds maximum size of {limit} bytes")
    resp = _s3.get_object(Bucket=UPLOADS_BUCKET, Key=object_key)
    return resp["Body"].read()


def delete_object(object_key: str, user_id: str) -> None:
    if object_key and object_key.startswith(user_prefix(user_id)):
        _s3.delete_object(Bucket=UPLOADS_BUCKET, Key=object_key)


def put_export_bytes(user_id: str, item_id: str, ext: str, data: bytes, content_type: str) -> str:
    key = f"exports/{user_id}/{item_id}/{ext}"
    _s3.put_object(
        Bucket=UPLOADS_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key
