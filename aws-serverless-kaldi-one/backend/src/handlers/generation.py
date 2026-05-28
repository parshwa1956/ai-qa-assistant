import json

from common import dynamodb as db, s3
from common.auth import require_user
from common.response import api_response, error_response
from handlers._router import parse_body
from services.openai_service import MAX_CONTEXT_CHARS, generate

MAX_REQUEST_BODY = 200000


def handler(event, context):
    try:
        user_id = require_user(event)
        raw_body = event.get("body") or ""
        if len(raw_body) > MAX_REQUEST_BODY:
            return error_response("Request body too large", 413, event=event)

        body = parse_body(event)
        workspace = body.get("workspace", "").strip()
        output_type = body.get("outputType", "").strip()
        title = body.get("title", "")
        context_text = body.get("context", "")
        project_id = body.get("projectId", "")
        object_key = body.get("objectKey")
        code_input = body.get("codeInput", "")

        if not workspace or not output_type:
            return error_response("workspace and outputType are required", 400, event=event)
        if len(context_text) > MAX_CONTEXT_CHARS:
            return error_response(f"context exceeds {MAX_CONTEXT_CHARS} characters", 400, event=event)

        image_bytes = None
        image_content_type = None
        source_filename = body.get("sourceFilename", "")

        if object_key:
            head_type = body.get("contentType", "application/octet-stream")
            raw = s3.get_object_bytes(object_key, user_id)
            if head_type.startswith("image/"):
                image_bytes = raw
                image_content_type = head_type
            elif head_type in ("text/plain", "text/markdown", "text/csv"):
                context_text = f"{context_text}\n\n--- File ---\n{raw.decode('utf-8', errors='ignore')[:15000]}"
            else:
                try:
                    context_text = f"{context_text}\n\n--- File ---\n{raw.decode('utf-8', errors='ignore')[:15000]}"
                except Exception:
                    pass

        if project_id and not db.get_project(user_id, project_id):
            return error_response("Invalid project", 400, event=event)

        result = generate(
            workspace=workspace,
            output_type=output_type,
            title=title,
            context=context_text,
            image_bytes=image_bytes,
            image_content_type=image_content_type,
            source_filename=source_filename,
            code_input=code_input,
        )

        return api_response(
            200,
            {
                **result,
                "projectId": project_id,
                "workspace": workspace,
            },
            event=event,
        )
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except ValueError as exc:
        return error_response(str(exc), 400, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
