import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr, Key

TABLE_NAME = os.environ.get("TABLE_NAME", "")
_dynamodb = boto3.resource("dynamodb")
_table = None


def get_table():
    global _table
    if _table is None:
        if not TABLE_NAME:
            raise RuntimeError("TABLE_NAME not configured")
        _table = _dynamodb.Table(TABLE_NAME)
    return _table


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pk_user(user_id: str) -> str:
    return f"USER#{user_id}"


def sk_profile() -> str:
    return "PROFILE"


def sk_project(project_id: str) -> str:
    return f"PROJECT#{project_id}"


def sk_item(created_at: str, item_id: str) -> str:
    return f"ITEM#{created_at}#{item_id}"


def sk_jira() -> str:
    return "JIRA"


def gsi1_project(user_id: str, project_id: str) -> tuple[str, str]:
    return f"USER#{user_id}#PROJECT#{project_id}", "ITEM"


def new_id() -> str:
    return str(uuid4())


def get_profile(user_id: str) -> Optional[dict]:
    resp = get_table().get_item(Key={"PK": pk_user(user_id), "SK": sk_profile()})
    return resp.get("Item")


def put_profile(user_id: str, email: str) -> dict:
    item = {
        "PK": pk_user(user_id),
        "SK": sk_profile(),
        "entityType": "PROFILE",
        "userId": user_id,
        "email": email,
        "createdAt": now_iso(),
        "bootstrapped": False,
    }
    get_table().put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(PK)",
    )
    return item


def mark_bootstrapped(user_id: str) -> None:
    get_table().update_item(
        Key={"PK": pk_user(user_id), "SK": sk_profile()},
        UpdateExpression="SET bootstrapped = :b, updatedAt = :u",
        ExpressionAttributeValues={":b": True, ":u": now_iso()},
    )


def list_projects(user_id: str) -> list[dict]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(pk_user(user_id))
        & Key("SK").begins_with("PROJECT#"),
    )
    items = resp.get("Items", [])
    return sorted(items, key=lambda x: x.get("updatedAt", ""), reverse=True)


def get_project(user_id: str, project_id: str) -> Optional[dict]:
    resp = get_table().get_item(Key={"PK": pk_user(user_id), "SK": sk_project(project_id)})
    return resp.get("Item")


def create_project(user_id: str, name: str) -> dict:
    project_id = new_id()
    ts = now_iso()
    item = {
        "PK": pk_user(user_id),
        "SK": sk_project(project_id),
        "entityType": "PROJECT",
        "projectId": project_id,
        "userId": user_id,
        "name": name.strip(),
        "isDefault": False,
        "createdAt": ts,
        "updatedAt": ts,
    }
    get_table().put_item(Item=item)
    return item


def create_general_project(user_id: str) -> dict:
    project_id = new_id()
    ts = now_iso()
    item = {
        "PK": pk_user(user_id),
        "SK": sk_project(project_id),
        "entityType": "PROJECT",
        "projectId": project_id,
        "userId": user_id,
        "name": "General",
        "isDefault": True,
        "createdAt": ts,
        "updatedAt": ts,
    }
    get_table().put_item(Item=item)
    return item


def update_project_name(user_id: str, project_id: str, name: str) -> dict:
    resp = get_table().update_item(
        Key={"PK": pk_user(user_id), "SK": sk_project(project_id)},
        UpdateExpression="SET #n = :name, updatedAt = :u",
        ExpressionAttributeNames={"#n": "name"},
        ConditionExpression="attribute_exists(PK) AND (attribute_not_exists(isDefault) OR isDefault <> :t)",
        ExpressionAttributeValues={
            ":name": name.strip(),
            ":u": now_iso(),
            ":t": True,
        },
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]


def delete_project(user_id: str, project_id: str) -> None:
    project = get_project(user_id, project_id)
    if not project:
        raise ValueError("Project not found")
    if project.get("isDefault") or project.get("name") == "General":
        raise ValueError("Cannot delete the default General project")

    items = list_items_for_project(user_id, project_id)
    with get_table().batch_writer() as batch:
        batch.delete_item(Key={"PK": pk_user(user_id), "SK": sk_project(project_id)})
        for it in items:
            batch.delete_item(Key={"PK": it["PK"], "SK": it["SK"]})


def save_history_item(user_id: str, payload: dict) -> dict:
    item_id = payload.get("itemId") or new_id()
    created_at = payload.get("createdAt") or now_iso()
    project_id = payload["projectId"]
    gsi_pk, gsi_sk_prefix = gsi1_project(user_id, project_id)

    item = {
        "PK": pk_user(user_id),
        "SK": sk_item(created_at, item_id),
        "GSI1PK": gsi_pk,
        "GSI1SK": f"{gsi_sk_prefix}#{created_at}#{item_id}",
        "entityType": "ITEM",
        "itemId": item_id,
        "userId": user_id,
        "projectId": project_id,
        "itemType": payload["itemType"],
        "title": payload.get("title", ""),
        "inputContext": payload.get("inputContext", ""),
        "outputText": payload.get("outputText", ""),
        "outputJson": payload.get("outputJson"),
        "mermaidCode": payload.get("mermaidCode"),
        "screenshotPath": payload.get("screenshotPath"),
        "sourceFilename": payload.get("sourceFilename", ""),
        "workspace": payload.get("workspace", ""),
        "createdAt": created_at,
    }
    get_table().put_item(Item=item)

    get_table().update_item(
        Key={"PK": pk_user(user_id), "SK": sk_project(project_id)},
        UpdateExpression="SET updatedAt = :u",
        ExpressionAttributeValues={":u": now_iso()},
    )
    return item


def get_history_item(user_id: str, item_id: str) -> Optional[dict]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(pk_user(user_id))
        & Key("SK").begins_with("ITEM#"),
        FilterExpression=Attr("itemId").eq(item_id),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def delete_history_item(user_id: str, item_id: str) -> Optional[dict]:
    item = get_history_item(user_id, item_id)
    if not item:
        return None
    get_table().delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
    return item


def list_items_for_project(user_id: str, project_id: str) -> list[dict]:
    gsi_pk, _ = gsi1_project(user_id, project_id)
    resp = get_table().query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(gsi_pk),
        ScanIndexForward=False,
    )
    return resp.get("Items", [])


def list_all_items(user_id: str, project_id: Optional[str] = None, item_type: Optional[str] = None) -> list[dict]:
    if project_id:
        items = list_items_for_project(user_id, project_id)
    else:
        resp = get_table().query(
            KeyConditionExpression=Key("PK").eq(pk_user(user_id))
            & Key("SK").begins_with("ITEM#"),
            ScanIndexForward=False,
        )
        items = resp.get("Items", [])
    if item_type:
        items = [i for i in items if i.get("itemType") == item_type]
    return sorted(items, key=lambda x: x.get("createdAt", ""), reverse=True)


def search_items(user_id: str, query: str, project_id: Optional[str] = None) -> list[dict]:
    q = query.lower().strip()
    items = list_all_items(user_id, project_id=project_id)
    if not q:
        return items
    results = []
    for it in items:
        hay = " ".join(
            [
                str(it.get("title", "")),
                str(it.get("itemType", "")),
                str(it.get("outputText", "")),
                str(it.get("inputContext", "")),
            ]
        ).lower()
        if q in hay:
            results.append(it)
    return results


def get_jira_config(user_id: str) -> Optional[dict]:
    resp = get_table().get_item(Key={"PK": pk_user(user_id), "SK": sk_jira()})
    item = resp.get("Item")
    if item:
        item.pop("jiraApiToken", None)
    return item


def save_jira_config(user_id: str, config: dict) -> dict:
    existing = get_table().get_item(Key={"PK": pk_user(user_id), "SK": sk_jira()}).get("Item")
    ts = now_iso()
    item = {
        "PK": pk_user(user_id),
        "SK": sk_jira(),
        "entityType": "JIRA",
        "userId": user_id,
        "jiraBaseUrl": config["jiraBaseUrl"].rstrip("/"),
        "jiraEmail": config["jiraEmail"].strip(),
        "jiraProjectKey": config["jiraProjectKey"].strip().upper(),
        "updatedAt": ts,
    }
    if config.get("jiraApiToken"):
        item["jiraApiToken"] = config["jiraApiToken"].strip()
    elif existing and existing.get("jiraApiToken"):
        item["jiraApiToken"] = existing["jiraApiToken"]
    else:
        raise ValueError("Jira API token is required on first save")

    if not existing:
        item["createdAt"] = ts
    get_table().put_item(Item=item)
    safe = dict(item)
    safe.pop("jiraApiToken", None)
    return safe


def delete_jira_config(user_id: str) -> None:
    get_table().delete_item(Key={"PK": pk_user(user_id), "SK": sk_jira()})


def get_jira_config_with_token(user_id: str) -> Optional[dict]:
    return get_table().get_item(Key={"PK": pk_user(user_id), "SK": sk_jira()}).get("Item")
