from common import dynamodb as db
from common.auth import require_user
from common.response import api_response, error_response


def handler(event, context):
    try:
        user_id = require_user(event)
        projects = db.list_projects(user_id)
        items = db.list_all_items(user_id)

        test_case_count = sum(1 for i in items if i.get("itemType") == "Test Cases")
        bug_count = sum(1 for i in items if i.get("itemType") == "Bug Report")

        recent_items = items[:8]
        recent_projects = projects[:5]

        return api_response(
            200,
            {
                "totalProjects": len(projects),
                "totalTestCases": test_case_count,
                "totalBugReports": bug_count,
                "totalItems": len(items),
                "recentProjects": [
                    {"projectId": p["projectId"], "name": p["name"], "updatedAt": p.get("updatedAt")}
                    for p in recent_projects
                ],
                "recentItems": [
                    {
                        "itemId": i["itemId"],
                        "title": i.get("title"),
                        "itemType": i.get("itemType"),
                        "projectId": i.get("projectId"),
                        "createdAt": i.get("createdAt"),
                    }
                    for i in recent_items
                ],
            },
            event=event,
        )
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)
