from botocore.exceptions import ClientError

from common import dynamodb as db
from common.auth import require_user
from common.response import api_response, error_response
from handlers._router import parse_body, path_param, route_key


def handler(event, context):
    try:
        user_id = require_user(event)
        method = event.get("requestContext", {}).get("http", {}).get("method") or event.get(
            "httpMethod", "GET"
        )
        rk = route_key(event)

        if method == "GET" or rk == "GET /projects":
            projects = db.list_projects(user_id)
            return api_response(200, {"projects": projects}, event=event)

        body = parse_body(event)

        if method == "POST":
            name = body.get("name", "").strip()
            if not name:
                return error_response("Project name is required", 400, event=event)
            project = db.create_project(user_id, name)
            return api_response(201, {"project": project}, event=event)

        project_id = path_param(event, "projectId")
        if not project_id:
            return error_response("projectId is required", 400, event=event)

        if method == "PUT":
            name = body.get("name", "").strip()
            if not name:
                return error_response("Project name is required", 400, event=event)
            try:
                updated = db.update_project_name(user_id, project_id, name)
            except ClientError:
                return error_response("Cannot rename default project or project not found", 400, event=event)
            return api_response(200, {"project": updated}, event=event)

        if method == "DELETE":
            try:
                db.delete_project(user_id, project_id)
            except ValueError as exc:
                return error_response(str(exc), 400, event=event)
            return api_response(200, {"deleted": True}, event=event)

        return error_response("Method not allowed", 405, event=event)
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
