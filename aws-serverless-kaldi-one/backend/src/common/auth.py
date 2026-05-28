from typing import Optional


def get_user_id(event: dict) -> Optional[str]:
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    return claims.get("sub") or claims.get("cognito:username")


def require_user(event: dict) -> str:
    user_id = get_user_id(event)
    if not user_id:
        raise PermissionError("Unauthorized")
    return user_id
