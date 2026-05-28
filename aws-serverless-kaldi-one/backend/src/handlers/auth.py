from botocore.exceptions import ClientError

from common import dynamodb as db
from common.auth import require_user
from common.response import api_response, error_response
from handlers._router import parse_body


def handler(event, context):
    try:
        user_id = require_user(event)
        claims = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("jwt", {})
            .get("claims", {})
        )
        email = claims.get("email", "")

        profile = db.get_profile(user_id)
        if not profile:
            try:
                db.put_profile(user_id, email)
                profile = db.get_profile(user_id)
            except ClientError:
                profile = db.get_profile(user_id)

        projects = db.list_projects(user_id)
        if not profile or not profile.get("bootstrapped"):
            has_general = any(p.get("name") == "General" for p in projects)
            if not has_general:
                db.create_general_project(user_id)
                projects = db.list_projects(user_id)
            if profile:
                db.mark_bootstrapped(user_id)

        return api_response(
            200,
            {
                "userId": user_id,
                "email": email,
                "projects": [
                    {
                        "projectId": p["projectId"],
                        "name": p["name"],
                        "isDefault": p.get("isDefault", False),
                        "createdAt": p.get("createdAt"),
                        "updatedAt": p.get("updatedAt"),
                    }
                    for p in projects
                ],
            },
            event=event,
        )
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
