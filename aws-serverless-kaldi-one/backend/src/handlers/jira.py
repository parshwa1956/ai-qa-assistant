from common import dynamodb as db
from common.auth import require_user
from common.response import api_response, error_response
from handlers._router import parse_body, route_key
from services.jira_service import create_issue, default_issue_type, default_labels, test_connection


def handler(event, context):
    try:
        user_id = require_user(event)
        method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

        if method == "GET":
            config = db.get_jira_config(user_id)
            return api_response(200, {"configured": bool(config), "config": config}, event=event)

        if method == "DELETE":
            db.delete_jira_config(user_id)
            return api_response(200, {"deleted": True}, event=event)

        body = parse_body(event)

        if method == "PUT":
            required = ["jiraBaseUrl", "jiraEmail", "jiraProjectKey"]
            for field in required:
                if not body.get(field):
                    return error_response(f"{field} is required", 400, event=event)
            saved = db.save_jira_config(user_id, body)
            return api_response(200, {"config": saved}, event=event)

        rk = route_key(event)
        if method == "POST" and rk == "POST /jira/test":
            token = body.get("jiraApiToken")
            if token:
                ok, msg = test_connection(body["jiraBaseUrl"], body["jiraEmail"], token)
            else:
                cfg = db.get_jira_config_with_token(user_id)
                if not cfg:
                    return error_response("Jira is not configured", 400, event=event)
                ok, msg = test_connection(cfg["jiraBaseUrl"], cfg["jiraEmail"], cfg["jiraApiToken"])
            return api_response(200 if ok else 400, {"success": ok, "message": msg}, event=event)

        if method == "POST" and rk == "POST /jira/issues":
            cfg = db.get_jira_config_with_token(user_id)
            if not cfg:
                return error_response("Configure Jira in Settings first", 400, event=event)

            summary = body.get("summary", "Kaldi One output")[:255]
            description = body.get("description", "")
            output_type = body.get("outputType", "Task")
            issue_type = body.get("issueType") or default_issue_type(output_type)
            labels = body.get("labels") or default_labels(output_type)

            ok, result = create_issue(
                cfg["jiraBaseUrl"],
                cfg["jiraEmail"],
                cfg["jiraApiToken"],
                cfg["jiraProjectKey"],
                summary,
                description,
                issue_type=issue_type,
                labels=labels,
            )
            return api_response(200 if ok else 400, {"success": ok, "issueKey": result if ok else None, "message": result}, event=event)

        return error_response("Method not allowed", 405, event=event)
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
