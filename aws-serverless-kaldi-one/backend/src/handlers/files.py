from common.auth import require_user
from common.response import api_response, error_response
from common import s3
from handlers._router import parse_body, query_param


def handler(event, context):
    try:
        user_id = require_user(event)
        method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

        if method == "POST":
            body = parse_body(event)
            filename = body.get("filename", "").strip()
            content_type = body.get("contentType", "").strip()
            project_id = body.get("projectId", "").strip()
            if not all([filename, content_type, project_id]):
                return error_response("filename, contentType, and projectId are required", 400, event=event)
            presigned = s3.presign_upload(user_id, project_id, filename, content_type)
            return api_response(200, presigned, event=event)

        if method == "GET":
            object_key = query_param(event, "objectKey")
            if not object_key:
                return error_response("objectKey is required", 400, event=event)
            url = s3.presign_download(object_key, user_id)
            return api_response(200, {"downloadUrl": url}, event=event)

        return error_response("Method not allowed", 405, event=event)
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except ValueError as exc:
        return error_response(str(exc), 400, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
