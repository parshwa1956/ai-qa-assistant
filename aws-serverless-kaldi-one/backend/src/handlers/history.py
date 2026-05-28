import json

from common import dynamodb as db, s3
from common.auth import require_user
from common.response import api_response, error_response
from handlers._router import parse_body, path_param, query_param
from services.export_service import export_csv, export_txt, export_xlsx, table_from_item


def handler(event, context):
    try:
        user_id = require_user(event)
        method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
        item_id = path_param(event, "itemId")

        if method == "GET":
            project_id = query_param(event, "projectId")
            item_type = query_param(event, "itemType")
            search = query_param(event, "q")
            if search:
                items = db.search_items(user_id, search, project_id=project_id)
            else:
                items = db.list_all_items(user_id, project_id=project_id, item_type=item_type)
            return api_response(200, {"items": _public_items(items)}, event=event)

        if method == "POST" and not item_id:
            body = parse_body(event)
            required = ["projectId", "itemType", "title"]
            for field in required:
                if not body.get(field):
                    return error_response(f"{field} is required", 400, event=event)
            if not db.get_project(user_id, body["projectId"]):
                return error_response("Invalid project", 400, event=event)
            saved = db.save_history_item(
                user_id,
                {
                    "projectId": body["projectId"],
                    "itemType": body["itemType"],
                    "title": body["title"],
                    "inputContext": body.get("inputContext", ""),
                    "outputText": body.get("outputText", ""),
                    "outputJson": body.get("outputJson"),
                    "mermaidCode": body.get("mermaidCode"),
                    "screenshotPath": body.get("screenshotPath"),
                    "sourceFilename": body.get("sourceFilename", ""),
                    "workspace": body.get("workspace", ""),
                },
            )
            return api_response(201, {"item": _public_item(saved)}, event=event)

        if method == "DELETE" and item_id:
            deleted = db.delete_history_item(user_id, item_id)
            if not deleted:
                return error_response("Item not found", 404, event=event)
            if deleted.get("screenshotPath"):
                s3.delete_object(deleted["screenshotPath"], user_id)
            return api_response(200, {"deleted": True}, event=event)

        if method == "POST" and item_id:
            body = parse_body(event)
            fmt = (body.get("format") or "txt").lower()
            item = db.get_history_item(user_id, item_id)
            if not item:
                return error_response("Item not found", 404, event=event)

            table = body.get("tableData") or table_from_item(item)
            output_text = item.get("outputText", "")
            title = item.get("title", "export")

            if fmt == "csv":
                data = export_csv(table, output_text)
                content_type = "text/csv"
                ext = "csv"
            elif fmt == "xlsx":
                data = export_xlsx(table, output_text, title)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ext = "xlsx"
            else:
                data = export_txt(output_text)
                content_type = "text/plain"
                ext = "txt"

            key = s3.put_export_bytes(user_id, item_id, ext, data, content_type)
            url = s3.presign_download(key, user_id)
            return api_response(200, {"downloadUrl": url, "format": fmt}, event=event)

        return error_response("Method not allowed", 405, event=event)
    except PermissionError:
        return error_response("Unauthorized", 401, event=event)
    except Exception as exc:
        return error_response(str(exc), 500, event=event)


def _public_item(item: dict) -> dict:
    out = dict(item)
    if isinstance(out.get("outputJson"), dict):
        out["outputJson"] = out["outputJson"]
    return out


def _public_items(items: list[dict]) -> list[dict]:
    return [_public_item(i) for i in items]
