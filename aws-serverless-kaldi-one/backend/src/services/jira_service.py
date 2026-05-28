import requests


def test_connection(base_url: str, email: str, api_token: str) -> tuple[bool, str]:
    if not all([base_url, email, api_token]):
        return False, "Complete Jira Base URL, Email, and API Token."
    url = f"{base_url.rstrip('/')}/rest/api/3/myself"
    try:
        resp = requests.get(url, headers={"Accept": "application/json"}, auth=(email, api_token), timeout=30)
    except Exception as exc:
        return False, f"Connection failed: {exc}"
    if resp.status_code == 200:
        data = resp.json()
        return True, f"Connected as {data.get('displayName', 'user')}"
    return False, resp.text[:500]


def build_adf_description(text: str) -> dict:
    paragraphs = []
    for line in (text or "").split("\n"):
        if line.strip():
            paragraphs.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}],
                }
            )
    if not paragraphs:
        paragraphs.append({"type": "paragraph", "content": [{"type": "text", "text": " "}]})
    return {"type": "doc", "version": 1, "content": paragraphs}


def default_issue_type(output_type: str) -> str:
    mapping = {
        "Bug Report": "Bug",
        "Test Cases": "Task",
        "Test Scenarios": "Task",
        "Smart Code Review": "Task",
    }
    return mapping.get(output_type, "Story")


def default_labels(output_type: str) -> list[str]:
    return ["kaldi-one", output_type.lower().replace(" ", "-")[:50]]


def create_issue(
    base_url: str,
    email: str,
    api_token: str,
    project_key: str,
    summary: str,
    description: str,
    issue_type: str | None = None,
    labels: list[str] | None = None,
) -> tuple[bool, str]:
    url = f"{base_url.rstrip('/')}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary[:255],
            "description": build_adf_description(description),
            "issuetype": {"name": issue_type or "Task"},
            "labels": labels or [],
        }
    }
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            auth=(email, api_token),
            timeout=60,
        )
    except Exception as exc:
        return False, f"Connection failed: {exc}"
    if resp.status_code in (200, 201):
        return True, resp.json().get("key", "Created")
    return False, resp.text[:800]
