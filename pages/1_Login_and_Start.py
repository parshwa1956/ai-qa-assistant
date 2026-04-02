import os
import json
import base64
from io import BytesIO
from datetime import datetime, timezone
from urllib.parse import quote, unquote

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

try:
    from components.code_review_ui import render_code_review_results
except Exception:
    def render_code_review_results(review_result):
        st.json(review_result)

try:
    from services.code_review_service import run_smart_code_review
except Exception:
    def run_smart_code_review(code_input):
        return {
            "summary": {
                "total_issues": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_health": "Unavailable"
            },
            "issues": []
        }

# ------------------------------
# Load environment
# ------------------------------
load_dotenv()

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="Kaldi One",
    page_icon="🧪",
    layout="wide",
)

# ------------------------------
# Clients / secrets
# ------------------------------
def get_secret_or_env(name: str, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


OPENAI_API_KEY = get_secret_or_env("OPENAI_API_KEY")
SUPABASE_URL = get_secret_or_env("SUPABASE_URL")
SUPABASE_KEY = get_secret_or_env("SUPABASE_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found in Streamlit secrets or .env.")
    st.stop()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL or SUPABASE_KEY not found in Streamlit secrets or .env.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = get_supabase()


def set_browser_cookie(name: str, value: str):
    safe_value = quote(value, safe="")
    components.html(
        f"""
        <script>
        document.cookie = "{name}={safe_value}; path=/; SameSite=Lax";
        </script>
        """,
        height=0,
        width=0,
    )


def delete_browser_cookie(name: str):
    components.html(
        f"""
        <script>
        document.cookie = "{name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
        </script>
        """,
        height=0,
        width=0,
    )


# ------------------------------
# Clean UI styling
# ------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    margin: 0 auto;
    padding-top: 3.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.hero-title {
    font-size: 2.3rem;
    font-weight: 700;
    color: #1f2937;
    margin-top: 0.1rem;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

.hero-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.clean-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
}

.result-card {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    background: #ffffff;
    padding: 1rem;
    margin-top: 1rem;
}

.small-muted {
    color: #6b7280;
    font-size: 0.86rem;
}

.mermaid-wrap {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 0.75rem;
    background: #fafafa;
    margin-bottom: 1rem;
}

section[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px;
}

section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stTextInput {
    margin-bottom: 0.35rem;
}

.top-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-top: 0.6rem;
    margin-bottom: 0.5rem;
}

.top-header-left {
    flex: 1;
    min-width: 0;
}

.top-header-right {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
    flex-wrap: nowrap;
    margin-top: 0.15rem;
}

.top-link-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-decoration: none !important;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1;
    white-space: nowrap;
    border: 1px solid #cbd5e1;
    transition: all 0.15s ease;
}

.top-link-btn.pro {
    background: #2563eb;
    color: #ffffff !important;
    border-color: #2563eb;
}

.top-link-btn.pro:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
}

.top-link-btn.support {
    background: #f8fafc;
    color: #334155 !important;
}

.top-link-btn.support:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
}

.top-link-btn.logout {
    background: #ffffff;
    color: #475569 !important;
}

.top-link-btn.logout:hover {
    background: #f8fafc;
    border-color: #94a3b8;
}

div.stButton > button[kind="primary"] {
    background: #2563eb;
    border-color: #2563eb;
}

div.stButton > button[kind="primary"]:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Session state init
# ------------------------------
def init_session_state():
    defaults = {
        "user": None,
        "access_token": None,
        "refresh_token": None,
        "selected_project_id": None,
        "generated_type": None,
        "generated_text": "",
        "generated_df": None,
        "generated_title": "",
        "generated_base_name": "",
        "generated_sheet_name": "",
        "generated_mermaid_code": "",
        "original_output_text": "",
        "editable_output_text": "",
        "original_output_df": None,
        "editable_output_df": None,
        "smart_review_result": None,
        "flow_generated_text": "",
        "flow_generated_title": "",
        "flow_generated_df": None,
        "flow_generated_base_name": "",
        "flow_generated_mermaid_code": "",
        "flow_uploaded_name": "",
        "flow_original_output_text": "",
        "flow_editable_output_text": "",
        "flow_original_output_df": None,
        "flow_editable_output_df": None,
        "auth_checked": False,
        "active_workspace": "QA Workspace",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# ------------------------------
# Copy / render helpers
# ------------------------------
def render_copy_button(text, button_label="Copy Output"):
    safe_text = json.dumps(text)
    components.html(
        f"""
        <button
            onclick='navigator.clipboard.writeText({safe_text})'
            style="
                background:#2563eb;
                color:white;
                border:none;
                border-radius:10px;
                padding:10px 16px;
                font-weight:600;
                cursor:pointer;
                width:100%;
            "
        >
            {button_label}
        </button>
        """,
        height=52,
    )


def build_mermaid_html_document(mermaid_code: str, title: str = "Diagram") -> str:
    safe_title = title.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_title}</title>
    <style>
        body {{
            margin: 0;
            padding: 24px;
            font-family: Arial, sans-serif;
            background: #ffffff;
        }}
        .diagram-shell {{
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            background: #ffffff;
            overflow: auto;
        }}
        .toolbar {{
            margin-bottom: 12px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        button {{
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            border-radius: 8px;
            padding: 8px 12px;
            cursor: pointer;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="window.print()">Print / Save as PDF</button>
        <button onclick="downloadSvg()">Download SVG</button>
    </div>
    <div class="diagram-shell">
        <div id="diagram_container" class="mermaid">
{mermaid_code}
        </div>
    </div>

    <script type="module">
        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
        mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});

        window.downloadSvg = function() {{
            const svg = document.querySelector("svg");
            if (!svg) {{
                alert("SVG not ready yet. Please wait a second and try again.");
                return;
            }}
            const blob = new Blob([svg.outerHTML], {{ type: "image/svg+xml;charset=utf-8" }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "{safe_filename(title)}.svg";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }};
    </script>
</body>
</html>
"""


def render_mermaid_diagram(mermaid_code: str, key_suffix: str, height: int = 500):
    if not mermaid_code.strip():
        return

    unique_id = f"mermaid_{safe_filename(key_suffix)}_{int(datetime.now().timestamp() * 1000)}"
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <style>
        body {{
            margin: 0;
            padding: 12px;
            background: white;
            font-family: Arial, sans-serif;
        }}
        .wrap {{
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 12px;
            background: #fafafa;
            overflow: auto;
        }}
        .mermaid {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="wrap">
        <div id="{unique_id}" class="mermaid">
{mermaid_code}
        </div>
    </div>

    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});
    </script>
</body>
</html>
"""

    components.html(
        html_content,
        height=height,
        scrolling=True,
    )


def show_mermaid_download_buttons(mermaid_code: str, base_name: str, diagram_title: str):
    if not mermaid_code.strip():
        return

    html_file = build_mermaid_html_document(mermaid_code, diagram_title)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            label="Download Mermaid Code (.mmd)",
            data=mermaid_code,
            file_name=f"{base_name}_diagram.mmd",
            mime="text/plain",
            use_container_width=True,
            key=f"download_mermaid_code_{base_name}",
        )
    with d2:
        st.download_button(
            label="Download Diagram HTML",
            data=html_file,
            file_name=f"{base_name}_diagram.html",
            mime="text/html",
            use_container_width=True,
            key=f"download_mermaid_html_{base_name}",
        )

    st.caption("Open the downloaded HTML file in your browser, then use Print / Save as PDF or Download SVG.")


# ------------------------------
# Utility helpers
# ------------------------------
def safe_filename(text):
    cleaned = "".join(c if c.isalnum() or c in (" ", "_", "-") else "" for c in text)
    cleaned = cleaned.strip().replace(" ", "_").lower()
    return cleaned if cleaned else "ai_output"


def encode_uploaded_image(uploaded_file):
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{encoded}"


def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def convert_df_to_excel(df, sheet_name="AI_Output"):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        header_fill = PatternFill(fill_type="solid", start_color="D9EAF7", end_color="D9EAF7")
        header_font = Font(bold=True)
        wrap_alignment = Alignment(wrap_text=True, vertical="top")

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = wrap_alignment

        for col_idx, column_cells in enumerate(worksheet.columns, start=1):
            max_length = 0
            col_letter = get_column_letter(col_idx)
            for cell in column_cells:
                cell.alignment = wrap_alignment
                try:
                    cell_value = str(cell.value) if cell.value is not None else ""
                    max_length = max(max_length, len(cell_value))
                except Exception:
                    pass
            adjusted_width = min(max(max_length + 2, 15), 60)
            worksheet.column_dimensions[col_letter].width = adjusted_width

        worksheet.freeze_panes = "A2"

    return output.getvalue()


def parse_json_response(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_uploaded_text_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return ""


# ------------------------------
# Auth helpers
# ------------------------------
def sign_up_user(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})


def sign_in_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})


PASSWORD_RESET_REDIRECT = get_secret_or_env("PASSWORD_RESET_REDIRECT", "http://localhost:8501")


def send_password_reset_email(email: str):
    return supabase.auth.reset_password_for_email(
        email,
        {"redirect_to": PASSWORD_RESET_REDIRECT},
    )


def update_logged_in_user_password(new_password: str):
    return supabase.auth.update_user({"password": new_password})


def auth_error_text(exc: Exception) -> str:
    text = str(exc)
    lower = text.lower()

    if "invalid login credentials" in lower:
        return "Unable to sign in. New user? Please use Sign Up. Already have an account? Use Forgot Password if needed."
    if "email not confirmed" in lower:
        return "Your account is created, but your email is not confirmed yet. Please check your inbox and confirm your email."
    if "user already registered" in lower:
        return "This account already exists. Please use Sign In or Forgot Password."
    if "invalid api key" in lower:
        return "Invalid Supabase configuration. Please check your Supabase URL and key in secrets.toml."
    return text


def handle_login_success(auth_response):
    if getattr(auth_response, "user", None):
        st.session_state.user = auth_response.user

    if getattr(auth_response, "session", None):
        st.session_state.access_token = auth_response.session.access_token
        st.session_state.refresh_token = auth_response.session.refresh_token
        set_browser_cookie("sb_access_token", auth_response.session.access_token)
        set_browser_cookie("sb_refresh_token", auth_response.session.refresh_token)

    upsert_profile(st.session_state.user)
    ensure_default_project(st.session_state.user.id)
    st.rerun()


def sign_out_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    delete_browser_cookie("sb_access_token")
    delete_browser_cookie("sb_refresh_token")

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    init_session_state()


def load_user_from_existing_session():
    try:
        access_token = st.context.cookies.get("sb_access_token")
        refresh_token = st.context.cookies.get("sb_refresh_token")

        if access_token:
            access_token = unquote(access_token)
        if refresh_token:
            refresh_token = unquote(refresh_token)

        if access_token and refresh_token:
            session_response = supabase.auth.set_session(access_token, refresh_token)

            if session_response and getattr(session_response, "user", None):
                st.session_state.user = session_response.user

            if session_response and getattr(session_response, "session", None):
                st.session_state.access_token = session_response.session.access_token
                st.session_state.refresh_token = session_response.session.refresh_token
                return

        session = supabase.auth.get_session()
        if session and getattr(session, "session", None):
            current_session = session.session
            if current_session and current_session.user:
                st.session_state.user = current_session.user
                st.session_state.access_token = current_session.access_token
                st.session_state.refresh_token = current_session.refresh_token
    except Exception:
        pass


# ------------------------------
# Database helpers
# ------------------------------
def upsert_profile(user):
    if not user:
        return
    payload = {"id": user.id, "email": user.email}
    return supabase.table("profiles").upsert(payload).execute()


def ensure_default_project(user_id: str):
    resp = (
        supabase.table("projects")
        .select("id,name")
        .eq("user_id", user_id)
        .eq("name", "General")
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        supabase.table("projects").insert(
            {
                "user_id": user_id,
                "name": "General",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            }
        ).execute()


def create_project(user_id: str, name: str):
    return (
        supabase.table("projects")
        .insert(
            {
                "user_id": user_id,
                "name": name.strip(),
                "created_at": now_iso(),
                "updated_at": now_iso(),
            }
        )
        .execute()
    )


def get_projects(user_id: str):
    return (
        supabase.table("projects")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )


def rename_project(project_id: str, user_id: str, new_name: str):
    return (
        supabase.table("projects")
        .update({"name": new_name.strip(), "updated_at": now_iso()})
        .eq("id", project_id)
        .eq("user_id", user_id)
        .execute()
    )


def get_project_by_id(project_id: str, user_id: str):
    resp = (
        supabase.table("projects")
        .select("*")
        .eq("id", project_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    return rows[0] if rows else None


def delete_project(project_id: str, user_id: str):
    project = get_project_by_id(project_id, user_id)
    if not project:
        return False, "Project not found."

    if project["name"] == "General":
        return False, "You cannot delete the default General project."

    items_resp = (
        supabase.table("saved_items")
        .select("id,screenshot_path")
        .eq("project_id", project_id)
        .eq("user_id", user_id)
        .execute()
    )
    items = items_resp.data or []

    for item in items:
        screenshot_path = item.get("screenshot_path")
        if screenshot_path:
            try:
                supabase.storage.from_("screenshots").remove([screenshot_path])
            except Exception:
                pass

    supabase.table("saved_items").delete().eq("project_id", project_id).eq("user_id", user_id).execute()
    supabase.table("projects").delete().eq("id", project_id).eq("user_id", user_id).execute()

    return True, f"Project '{project['name']}' deleted."


def save_item(
    user_id: str,
    project_id: str,
    item_type: str,
    title: str,
    input_context: str,
    output_text: str,
    screenshot_path: str = None,
    source_filename: str = None,
):
    supabase.table("projects").update({"updated_at": now_iso()}).eq("id", project_id).eq("user_id", user_id).execute()

    payload = {
        "user_id": user_id,
        "project_id": project_id,
        "item_type": item_type,
        "title": title.strip(),
        "input_context": input_context.strip(),
        "output_text": output_text.strip(),
        "screenshot_path": screenshot_path,
        "source_filename": source_filename,
        "created_at": now_iso(),
    }
    return supabase.table("saved_items").insert(payload).execute()


def get_project_items(user_id: str, project_id: str):
    resp = (
        supabase.table("saved_items")
        .select("*")
        .eq("user_id", user_id)
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def get_jira_integration(user_id: str):
    resp = (
        supabase.table("jira_integrations")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    return rows[0] if rows else None


# ------------------------------
# Storage helpers
# ------------------------------
def upload_screenshot_to_storage(user_id: str, project_id: str, uploaded_file):
    if uploaded_file is None:
        return None

    ext = os.path.splitext(uploaded_file.name)[1] or ".bin"
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    storage_path = f"{user_id}/{project_id}/{filename}"

    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    supabase.storage.from_("screenshots").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": uploaded_file.type},
    )
    return storage_path


# ------------------------------
# Jira helpers
# ------------------------------
def get_default_jira_issue_type(output_type):
    mapping = {
        "Bug Report": "Bug",
        "Test Cases": "Task",
        "Test Scenarios": "Story",
        "Requirement to User Story": "Story",
        "Acceptance Criteria Generator": "Task",
        "Business Requirement Breakdown": "Task",
        "Business Process Flow": "Task",
        "Data Flow Diagram": "Task",
        "Technical Task Breakdown": "Task",
        "API / Backend Tasks": "Task",
        "Developer Checklist": "Task",
        "Smart Code Review": "Bug",
        "Technical Flow Diagram": "Task",
    }
    return mapping.get(output_type, "Task")


def get_default_jira_labels(output_type):
    mapping = {
        "Bug Report": ["bug"],
        "Test Cases": ["task"],
        "Test Scenarios": ["story"],
        "Requirement to User Story": ["story"],
        "Acceptance Criteria Generator": ["acceptance-criteria"],
        "Business Requirement Breakdown": ["business-requirement"],
        "Business Process Flow": ["process-flow"],
        "Data Flow Diagram": ["data-flow"],
        "Technical Task Breakdown": ["technical-task"],
        "API / Backend Tasks": ["api-task"],
        "Developer Checklist": ["developer-checklist"],
        "Smart Code Review": ["code-review"],
        "Technical Flow Diagram": ["technical-flow"],
    }
    return mapping.get(output_type, ["task"])


def build_jira_description_doc(description_text):
    lines = [line.strip() for line in description_text.splitlines() if line.strip()]

    content_blocks = []
    for line in lines:
        content_blocks.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line[:3000]}],
            }
        )

    if not content_blocks:
        content_blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "No description provided."}],
            }
        ]

    return {"type": "doc", "version": 1, "content": content_blocks}


def create_jira_issue(
    jira_base_url,
    jira_email,
    jira_api_token,
    jira_project_key,
    summary,
    description,
    issue_type="Task",
    labels=None,
):
    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        return False, "Jira settings are missing. Please connect your Jira account first."

    url = f"{jira_base_url.rstrip('/')}/rest/api/3/issue"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (jira_email, jira_api_token)

    payload = {
        "fields": {
            "project": {"key": jira_project_key},
            "summary": summary,
            "description": build_jira_description_doc(description),
            "issuetype": {"name": issue_type},
            "labels": labels or [],
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=60)
    except Exception as e:
        return False, f"Connection failed: {e}"

    if response.status_code in [200, 201]:
        data = response.json()
        return True, data.get("key", "Created")

    return False, response.text


# ------------------------------
# OpenAI generators
# ------------------------------
def generate_bug_report_with_optional_image(title, context, uploaded_file):
    text_prompt = f"""
You are a senior QA engineer.

Generate a professional bug report for the following issue.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "bug_report": {{
    "Title": "",
    "Description": "",
    "Steps to Reproduce": "",
    "Expected Result": "",
    "Actual Result": "",
    "Severity": "",
    "Priority": "",
    "Environment": "",
    "Observed UI / Screenshot Notes": "",
    "Assumptions": ""
  }}
}}
"""

    if uploaded_file is not None:
        image_data_url = encode_uploaded_image(uploaded_file)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                }
            ],
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text_prompt}],
        )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    bug_report = parsed["bug_report"]

    pretty_text = "\n".join([f"{k}: {v}" for k, v in bug_report.items()])
    df = pd.DataFrame([bug_report])

    return pretty_text, df


def generate_test_cases(title, context):
    prompt = f"""
You are a senior QA engineer.

Generate detailed QA test cases for the following issue, feature, or requirement.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "test_cases": [
    {{
      "Test Case ID": "TC_001",
      "Category": "Functional",
      "Scenario": "",
      "Preconditions": "",
      "Steps": "",
      "Expected Result": "",
      "Priority": "",
      "Type": "Positive"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    test_cases = parsed["test_cases"]

    pretty_lines = []
    for tc in test_cases:
        pretty_lines.append(
            f"""Test Case ID: {tc.get('Test Case ID', '')}
Category: {tc.get('Category', '')}
Scenario: {tc.get('Scenario', '')}
Preconditions: {tc.get('Preconditions', '')}
Steps: {tc.get('Steps', '')}
Expected Result: {tc.get('Expected Result', '')}
Priority: {tc.get('Priority', '')}
Type: {tc.get('Type', '')}
"""
        )

    pretty_text = "\n" + ("\n" + "-" * 80 + "\n").join(pretty_lines)
    df = pd.DataFrame(test_cases)

    return pretty_text, df


def generate_test_scenarios(title, context):
    prompt = f"""
You are a senior QA engineer.

Generate high-level test scenarios based on the following business requirement, feature, or issue.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "test_scenarios": [
    {{
      "Scenario ID": "TS_001",
      "Category": "Functional",
      "Scenario": "",
      "Description": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    scenarios = parsed["test_scenarios"]

    pretty_lines = []
    for sc in scenarios:
        pretty_lines.append(
            f"""Scenario ID: {sc.get('Scenario ID', '')}
Category: {sc.get('Category', '')}
Scenario: {sc.get('Scenario', '')}
Description: {sc.get('Description', '')}
Priority: {sc.get('Priority', '')}
Notes: {sc.get('Notes', '')}
"""
        )

    pretty_text = "\n" + ("\n" + "-" * 80 + "\n").join(pretty_lines)
    df = pd.DataFrame(scenarios)

    return pretty_text, df


def generate_ba_output(title, context, output_type):
    prompt_map = {
        "Requirement to User Story": f"""
You are a senior business analyst.

Convert the following requirement into structured user stories.

Title: {title}
Requirement Details: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "user_stories": [
    {{
      "User Story ID": "US_001",
      "As a": "",
      "I want": "",
      "So that": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
""",
        "Acceptance Criteria Generator": f"""
You are a senior business analyst.

Generate clear acceptance criteria for the following requirement.

Title: {title}
Requirement Details: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "acceptance_criteria": [
    {{
      "AC ID": "AC_001",
      "Criteria": "",
      "Type": "",
      "Priority": ""
    }}
  ]
}}
""",
        "Business Requirement Breakdown": f"""
You are a senior business analyst.

Break down the following requirement into structured business requirement points.

Title: {title}
Requirement Details: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "requirement_breakdown": [
    {{
      "Section": "",
      "Details": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
""",
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_map[output_type]}],
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)

    if output_type == "Requirement to User Story":
        records = parsed["user_stories"]
        pretty = "\n\n".join(
            [
                f"""User Story ID: {r.get('User Story ID', '')}
As a: {r.get('As a', '')}
I want: {r.get('I want', '')}
So that: {r.get('So that', '')}
Priority: {r.get('Priority', '')}
Notes: {r.get('Notes', '')}"""
                for r in records
            ]
        )
    elif output_type == "Acceptance Criteria Generator":
        records = parsed["acceptance_criteria"]
        pretty = "\n\n".join(
            [
                f"""AC ID: {r.get('AC ID', '')}
Criteria: {r.get('Criteria', '')}
Type: {r.get('Type', '')}
Priority: {r.get('Priority', '')}"""
                for r in records
            ]
        )
    else:
        records = parsed["requirement_breakdown"]
        pretty = "\n\n".join(
            [
                f"""Section: {r.get('Section', '')}
Details: {r.get('Details', '')}
Priority: {r.get('Priority', '')}
Notes: {r.get('Notes', '')}"""
                for r in records
            ]
        )

    df = pd.DataFrame(records)
    return pretty, df


def generate_dev_output(title, context, output_type):
    prompt_map = {
        "Technical Task Breakdown": f"""
You are a senior software engineer.

Break down the following requirement into technical development tasks.

Title: {title}
Technical Context: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "technical_tasks": [
    {{
      "Task ID": "DEV_001",
      "Task": "",
      "Component": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
""",
        "API / Backend Tasks": f"""
You are a senior backend engineer.

Generate backend and API development tasks for the following requirement.

Title: {title}
Technical Context: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "api_tasks": [
    {{
      "Task ID": "API_001",
      "Task": "",
      "Endpoint / Service": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
""",
        "Developer Checklist": f"""
You are a senior software engineer.

Generate a developer checklist for the following requirement.

Title: {title}
Technical Context: {context}

Return ONLY valid JSON.
Do not add markdown.

Use this exact JSON structure:
{{
  "developer_checklist": [
    {{
      "Checklist Item": "",
      "Category": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}
""",
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_map[output_type]}],
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)

    if output_type == "Technical Task Breakdown":
        records = parsed["technical_tasks"]
        pretty = "\n\n".join(
            [
                f"""Task ID: {r.get('Task ID', '')}
Task: {r.get('Task', '')}
Component: {r.get('Component', '')}
Priority: {r.get('Priority', '')}
Notes: {r.get('Notes', '')}"""
                for r in records
            ]
        )
    elif output_type == "API / Backend Tasks":
        records = parsed["api_tasks"]
        pretty = "\n\n".join(
            [
                f"""Task ID: {r.get('Task ID', '')}
Task: {r.get('Task', '')}
Endpoint / Service: {r.get('Endpoint / Service', '')}
Priority: {r.get('Priority', '')}
Notes: {r.get('Notes', '')}"""
                for r in records
            ]
        )
    else:
        records = parsed["developer_checklist"]
        pretty = "\n\n".join(
            [
                f"""Checklist Item: {r.get('Checklist Item', '')}
Category: {r.get('Category', '')}
Priority: {r.get('Priority', '')}
Notes: {r.get('Notes', '')}"""
                for r in records
            ]
        )

    df = pd.DataFrame(records)
    return pretty, df


def generate_flow_diagram_output(title, context, diagram_type):
    prompt = f"""
You are a senior business systems analyst and solution architect.

Based on the requirement below, generate a {diagram_type}.

Title: {title}
Requirement Details: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation outside JSON.

Use this exact JSON structure:
{{
  "diagram_output": {{
    "diagram_type": "{diagram_type}",
    "mermaid_code": "flowchart TD\\n    A[Start] --> B[Process]",
    "steps": [
      {{
        "Step ID": "STEP_001",
        "From": "",
        "To": "",
        "Action": "",
        "Decision": "",
        "Notes": ""
      }}
    ]
  }}
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    diagram_output = parsed["diagram_output"]
    mermaid_code = diagram_output.get("mermaid_code", "")
    steps = diagram_output.get("steps", [])

    pretty_text = f"""Diagram Type: {diagram_output.get('diagram_type', diagram_type)}

Mermaid Code:
{mermaid_code}
"""
    df = pd.DataFrame(steps)
    return pretty_text, df, mermaid_code


def reset_flow_output_if_new_file(uploaded_flow):
    if uploaded_flow is None:
        return

    if st.session_state.flow_uploaded_name != uploaded_flow.name:
        clear_flow_output_state()
        st.session_state.flow_uploaded_name = uploaded_flow.name


def generate_requirements_from_flow(uploaded_flow):
    prompt = """
Analyze this flow diagram and generate concise business requirements.

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{
  "requirements": {
    "Process Summary": "",
    "What Happens from Start to Finish": [
      "Step 1",
      "Step 2",
      "Step 3"
    ],
    "Important Decisions": [
      "Decision 1",
      "Decision 2"
    ],
    "Test Data Needed": [
      "Data Point 1",
      "Data Point 2"
    ]
  }
}
"""

    if uploaded_flow.type in ["image/png", "image/jpg", "image/jpeg"]:
        image_data_url = encode_uploaded_image(uploaded_flow)
        uploaded_flow.seek(0)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                }
            ],
        )
        content = response.choices[0].message.content

    elif uploaded_flow.type == "application/pdf":
        file_bytes = uploaded_flow.read()
        uploaded_flow.seek(0)

        uploaded_pdf = client.files.create(
            file=(uploaded_flow.name, file_bytes, "application/pdf"),
            purpose="user_data",
        )

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_file", "file_id": uploaded_pdf.id},
                    ],
                }
            ],
        )

        content = response.output_text
    else:
        raise ValueError("Unsupported file type. Please upload PNG, JPG, JPEG, or PDF.")

    parsed = parse_json_response(content)
    req = parsed["requirements"]

    steps_text = "\n".join([f"{idx + 1}. {step}" for idx, step in enumerate(req.get("What Happens from Start to Finish", []))])
    decisions_text = "\n".join([f"- {item}" for item in req.get("Important Decisions", [])])
    test_data_text = "\n".join([f"- {item}" for item in req.get("Test Data Needed", [])])

    pretty_text = f"""Process Summary:
{req.get('Process Summary', '')}

What Happens from Start to Finish:
{steps_text}

Important Decisions:
{decisions_text}

Test Data Needed:
{test_data_text}
"""

    df = pd.DataFrame(
        [
            {
                "Process Summary": req.get("Process Summary", ""),
                "What Happens from Start to Finish": steps_text,
                "Important Decisions": decisions_text,
                "Test Data Needed": test_data_text,
            }
        ]
    )

    return pretty_text, df


# ------------------------------
# Output / render helpers
# ------------------------------
def show_download_buttons(df, pretty_text, base_name, sheet_name):
    csv_data = convert_df_to_csv(df)
    excel_data = convert_df_to_excel(df, sheet_name=sheet_name)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download TXT",
            data=pretty_text,
            file_name=f"{base_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{base_name}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"{base_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def dataframe_to_pretty_text(df: pd.DataFrame, output_type: str, mermaid_code: str = "") -> str:
    working_df = df.copy()

    if "Select" in working_df.columns:
        working_df = working_df.drop(columns=["Select"])

    records = working_df.to_dict(orient="records")

    if output_type == "Bug Report":
        if not records:
            return ""
        return "\n".join([f"{k}: {v}" for k, v in records[0].items()])

    blocks = []
    for row in records:
        block = "\n".join([f"{k}: {v}" for k, v in row.items()])
        blocks.append(block)

    body = "\n\n" + ("\n" + "-" * 80 + "\n").join(blocks) if blocks else ""

    if mermaid_code:
        return f"Mermaid Code:\n{mermaid_code}\n\nStructured Steps:{body}"

    return body


def set_current_output(output_type, title, result_text, df, base_name, sheet_name, mermaid_code=""):
    editable_df = df.copy()

    if output_type != "Bug Report" and "Select" not in editable_df.columns:
        editable_df.insert(0, "Select", False)

    st.session_state.generated_type = output_type
    st.session_state.generated_title = title
    st.session_state.generated_text = result_text
    st.session_state.generated_df = df
    st.session_state.generated_base_name = base_name
    st.session_state.generated_sheet_name = sheet_name
    st.session_state.generated_mermaid_code = mermaid_code
    st.session_state.original_output_text = result_text
    st.session_state.editable_output_text = result_text
    st.session_state.original_output_df = df.copy()
    st.session_state.editable_output_df = editable_df
    st.session_state.smart_review_result = None


def set_smart_code_review_output(title: str, review_result: dict):
    st.session_state.generated_type = "Smart Code Review"
    st.session_state.generated_title = title
    st.session_state.generated_text = json.dumps(review_result, indent=2)
    st.session_state.generated_df = None
    st.session_state.generated_base_name = f"{safe_filename(title)}_smart_code_review"
    st.session_state.generated_sheet_name = "Smart_Code_Review"
    st.session_state.generated_mermaid_code = ""
    st.session_state.original_output_text = st.session_state.generated_text
    st.session_state.editable_output_text = st.session_state.generated_text
    st.session_state.original_output_df = None
    st.session_state.editable_output_df = None
    st.session_state.smart_review_result = review_result


def build_row_summary(row_dict: dict, output_type: str, fallback_title: str) -> str:
    candidates = {
        "Bug Report": ["Title"],
        "Test Cases": ["Scenario", "Test Case ID", "Title"],
        "Test Scenarios": ["Scenario", "Scenario ID", "Title"],
        "Requirement to User Story": ["I want", "User Story ID", "Section"],
        "Acceptance Criteria Generator": ["Criteria", "AC ID"],
        "Business Requirement Breakdown": ["Section", "Details"],
        "Business Process Flow": ["Action", "Step ID"],
        "Data Flow Diagram": ["Action", "Step ID"],
        "Technical Task Breakdown": ["Task", "Task ID"],
        "API / Backend Tasks": ["Task", "Task ID", "Endpoint / Service"],
        "Developer Checklist": ["Checklist Item", "Category"],
        "Smart Code Review": ["Issue", "Issue ID"],
        "Technical Flow Diagram": ["Action", "Step ID"],
    }

    for key in candidates.get(output_type, []):
        value = str(row_dict.get(key, "")).strip()
        if value:
            return value[:200]

    for value in row_dict.values():
        text = str(value).strip()
        if text:
            return text[:200]

    return fallback_title


def render_row_level_jira(output_type: str, generated_title: str, edited_df: pd.DataFrame):
    jira_config = get_jira_integration(st.session_state.user.id) if st.session_state.user else None
    st.markdown("### Create in Jira")

    issue_type_options = ["Bug", "Task", "Story"]
    default_issue_type = get_default_jira_issue_type(output_type)
    default_labels = get_default_jira_labels(output_type)
    default_index = issue_type_options.index(default_issue_type) if default_issue_type in issue_type_options else 0

    jira_issue_type = st.selectbox(
        "Issue Type",
        issue_type_options,
        index=default_index,
        key=f"jira_issue_type_{output_type}",
    )

    if not jira_config:
        st.info("Open Settings page to connect JIRA.")
        return

    st.success(
        f"Connected: {jira_config.get('jira_base_url')} / {jira_config.get('jira_project_key')}"
    )

    selectable_df = edited_df.copy()

    if "Select" in selectable_df.columns:
        selected_rows = selectable_df[selectable_df["Select"] == True].drop(columns=["Select"], errors="ignore")
    else:
        selected_rows = selectable_df

    if st.button("Create Jira for Selected Rows", use_container_width=True, key=f"create_jira_rows_{output_type}"):
        if selected_rows.empty:
            st.warning("Please select at least one row.")
            return

        created_keys = []
        failed_rows = []

        with st.spinner("Creating Jira issues..."):
            for _, row in selected_rows.iterrows():
                row_dict = row.to_dict()
                summary = build_row_summary(row_dict, output_type, generated_title)
                description = "\n".join([f"{k}: {v}" for k, v in row_dict.items()])

                success, message = create_jira_issue(
                    jira_base_url=jira_config["jira_base_url"],
                    jira_email=jira_config["jira_email"],
                    jira_api_token=jira_config["jira_api_token"],
                    jira_project_key=jira_config["jira_project_key"],
                    summary=summary,
                    description=description,
                    issue_type=jira_issue_type,
                    labels=default_labels,
                )

                if success:
                    created_keys.append(message)
                else:
                    failed_rows.append(f"{summary}: {message}")

        if created_keys:
            st.success(f"Created {len(created_keys)} Jira issue(s): {', '.join(created_keys)}")
        if failed_rows:
            st.error("Some Jira issues failed:\n\n" + "\n".join(failed_rows))


def render_single_jira(output_type: str, generated_title: str, description_text: str):
    jira_config = get_jira_integration(st.session_state.user.id) if st.session_state.user else None
    st.markdown("### Create in Jira")

    issue_type_options = ["Bug", "Task", "Story"]
    default_issue_type = get_default_jira_issue_type(output_type)
    default_labels = get_default_jira_labels(output_type)
    default_index = issue_type_options.index(default_issue_type) if default_issue_type in issue_type_options else 0

    jira_issue_type = st.selectbox(
        "Issue Type",
        issue_type_options,
        index=default_index,
        key=f"jira_issue_type_{output_type}",
    )

    if not jira_config:
        st.info("Open Settings page to connect JIRA.")
        return

    st.success(
        f"Connected: {jira_config.get('jira_base_url')} / {jira_config.get('jira_project_key')}"
    )

    if st.button("Create in Jira", use_container_width=True, key=f"create_jira_{output_type}"):
        with st.spinner("Creating Jira issue..."):
            success, message = create_jira_issue(
                jira_base_url=jira_config["jira_base_url"],
                jira_email=jira_config["jira_email"],
                jira_api_token=jira_config["jira_api_token"],
                jira_project_key=jira_config["jira_project_key"],
                summary=generated_title,
                description=description_text,
                issue_type=jira_issue_type,
                labels=default_labels,
            )

        if success:
            issue_url = f"{jira_config['jira_base_url'].rstrip('/')}/browse/{message}"
            st.success(f"Jira issue created successfully: {message}")
            st.markdown(f"[Open Jira Issue]({issue_url})")
        else:
            st.error(f"Failed to create Jira issue: {message}")


def render_current_output():
    if st.session_state.generated_type == "Smart Code Review" and st.session_state.smart_review_result:
        st.subheader("Generated Smart Code Review")
        render_code_review_results(st.session_state.smart_review_result)

        json_text = json.dumps(st.session_state.smart_review_result, indent=2)
        st.download_button(
            label="Download Smart Code Review JSON",
            data=json_text,
            file_name=f"{st.session_state.generated_base_name}.json",
            mime="application/json",
            use_container_width=True,
            key="download_smart_code_review_json",
        )
        return

    if st.session_state.generated_type and st.session_state.editable_output_df is not None:
        output_type = st.session_state.generated_type
        generated_title = st.session_state.generated_title
        base_name = st.session_state.generated_base_name
        sheet_name = st.session_state.generated_sheet_name
        mermaid_code = st.session_state.generated_mermaid_code

        st.subheader(f"Generated {output_type}")

        if mermaid_code:
            st.markdown("#### Diagram Preview")
            render_mermaid_diagram(mermaid_code, output_type)
            show_mermaid_download_buttons(mermaid_code, base_name, generated_title)

        edited_df = st.data_editor(
            st.session_state.editable_output_df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{output_type}",
        )
        st.session_state.editable_output_df = edited_df

        edited_text = st.text_area(
            "Edit Output",
            value=st.session_state.editable_output_text,
            height=320,
            key="editable_output_box",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            render_copy_button(edited_text, "Copy Output")

        with c2:
            if st.button("Update Output", use_container_width=True, key="update_output_btn"):
                st.session_state.generated_text = edited_text
                st.session_state.editable_output_text = edited_text
                st.success("Output updated successfully.")

        with c3:
            if st.button("Reset Output", use_container_width=True, key="reset_output_btn"):
                st.session_state.generated_text = st.session_state.original_output_text
                st.session_state.editable_output_text = st.session_state.original_output_text
                st.session_state.editable_output_df = st.session_state.original_output_df.copy()
                st.rerun()

        final_text_from_grid = dataframe_to_pretty_text(
            st.session_state.editable_output_df,
            output_type,
            mermaid_code=mermaid_code,
        )

        show_download_buttons(
            st.session_state.editable_output_df.drop(columns=["Select"], errors="ignore"),
            final_text_from_grid,
            base_name,
            sheet_name,
        )

        if output_type == "Bug Report":
            render_single_jira(output_type, generated_title, st.session_state.editable_output_text)
        else:
            render_row_level_jira(output_type, generated_title, st.session_state.editable_output_df)


def render_flow_output():
    if st.session_state.flow_generated_df is not None:
        st.subheader("Generated Requirements")

        edited_flow_df = st.data_editor(
            st.session_state.flow_editable_output_df,
            use_container_width=True,
            num_rows="dynamic",
            key="flow_data_editor",
        )
        st.session_state.flow_editable_output_df = edited_flow_df

        edited_flow_text = st.text_area(
            "Edit Output",
            value=st.session_state.flow_editable_output_text,
            height=320,
            key="flow_editable_output_box",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            render_copy_button(edited_flow_text, "Copy Output")

        with c2:
            if st.button("Update Output", use_container_width=True, key="update_flow_output_btn"):
                st.session_state.flow_generated_text = edited_flow_text
                st.session_state.flow_editable_output_text = edited_flow_text
                st.success("Flow output updated successfully.")

        with c3:
            if st.button("Reset Output", use_container_width=True, key="reset_flow_output_btn"):
                st.session_state.flow_generated_text = st.session_state.flow_original_output_text
                st.session_state.flow_editable_output_text = st.session_state.flow_original_output_text
                st.session_state.flow_editable_output_df = st.session_state.flow_original_output_df.copy()
                st.rerun()

        flow_download_text = dataframe_to_pretty_text(
            st.session_state.flow_editable_output_df,
            "Flow Requirements",
            mermaid_code=st.session_state.flow_generated_mermaid_code,
        )

        show_download_buttons(
            st.session_state.flow_editable_output_df.drop(columns=["Select"], errors="ignore"),
            flow_download_text,
            st.session_state.flow_generated_base_name,
            "Flow_Requirements",
        )


# ------------------------------
# Sidebar
# ------------------------------
def render_sidebar_projects(user):
    st.sidebar.markdown("### Project")

    projects = get_projects(user.id).data or []

    if not projects:
        ensure_default_project(user.id)
        projects = get_projects(user.id).data or []

    if not st.session_state.selected_project_id and projects:
        st.session_state.selected_project_id = projects[0]["id"]

    selected_project = next(
        (p for p in projects if p["id"] == st.session_state.selected_project_id),
        projects[0] if projects else None,
    )

    if selected_project:
        project_names = [p["name"] for p in projects]
        current_index = next(
            (idx for idx, p in enumerate(projects) if p["id"] == selected_project["id"]),
            0,
        )

        selected_name = st.sidebar.selectbox(
            "Select Project",
            project_names,
            index=current_index,
            key="sidebar_selected_project_box",
        )

        selected_project = next((p for p in projects if p["name"] == selected_name), projects[0])
        st.session_state.selected_project_id = selected_project["id"]

    with st.sidebar.expander("Project Actions", expanded=False):
        new_project = st.text_input(
            "New project",
            placeholder="Example: Salesforce Regression",
            key="sidebar_new_project_name",
        )

        if st.button("Add Project", use_container_width=True, key="sidebar_add_project_btn"):
            project_name = new_project.strip()
            if not project_name:
                st.warning("Enter a project name.")
            else:
                if any(p["name"].lower() == project_name.lower() for p in projects):
                    st.warning("Project already exists.")
                else:
                    create_project(user.id, project_name)
                    created = get_projects(user.id).data or []
                    match = next((p for p in created if p["name"] == project_name), None)
                    if match:
                        st.session_state.selected_project_id = match["id"]
                    st.rerun()

        if selected_project:
            rename_value = st.text_input(
                "Rename selected project",
                value="" if selected_project["name"] == "General" else selected_project["name"],
                key="sidebar_rename_project_value",
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Rename", use_container_width=True, key="sidebar_rename_project_btn"):
                    new_name = rename_value.strip()
                    if not new_name:
                        st.warning("Enter a new project name.")
                    elif selected_project["name"] == "General":
                        st.warning("You cannot rename the default General project.")
                    elif any(p["name"].lower() == new_name.lower() and p["id"] != selected_project["id"] for p in projects):
                        st.warning("A project with that name already exists.")
                    else:
                        rename_project(selected_project["id"], user.id, new_name)
                        st.success(f"Project renamed to '{new_name}'.")
                        st.rerun()

            with c2:
                if st.button("Delete", use_container_width=True, key="sidebar_delete_project_btn"):
                    success, msg = delete_project(selected_project["id"], user.id)
                    if success:
                        st.session_state.selected_project_id = None
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning(msg)

    project_items = get_project_items(user.id, selected_project["id"]) if selected_project else []
    return projects, selected_project, project_items


# ------------------------------
# Auth screen
# ------------------------------
def render_auth_screen():
    st.markdown('<div class="hero-title">Kaldi One</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">AI-powered workspace for QA, BA, Development, and flow-based requirements.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not email.strip() or not password.strip():
                    st.error("Please enter email and password.")
                else:
                    try:
                        response = sign_in_user(email.strip(), password)
                        handle_login_success(response)
                    except Exception as e:
                        st.error(f"Login failed: {auth_error_text(e)}")

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            submit = st.form_submit_button("Create Account", use_container_width=True)

            if submit:
                if not email.strip() or not password.strip():
                    st.error("Please enter email and password.")
                else:
                    email = email.strip()
                    password = password.strip()

                    try:
                        existing_login = sign_in_user(email, password)
                        if getattr(existing_login, "session", None):
                            st.warning("This account is already created. Please use Sign In.")
                        else:
                            st.info("This account already exists. Please sign in, confirm your email, or use Forgot Password.")
                    except Exception:
                        try:
                            signup_response = sign_up_user(email, password)
                            if getattr(signup_response, "session", None):
                                st.success("Account created successfully.")
                            else:
                                st.success("Account created successfully. Please confirm your email, then sign in.")
                        except Exception as signup_exc:
                            st.error(f"Sign up failed: {auth_error_text(signup_exc)}")

    with tab3:
        with st.form("forgot_password_form"):
            email = st.text_input("Email", key="forgot_email")
            submit = st.form_submit_button("Send Reset Link", use_container_width=True)

            if submit:
                if not email.strip():
                    st.error("Please enter your email.")
                else:
                    try:
                        send_password_reset_email(email.strip())
                        st.success("Password reset email sent. Please check your inbox.")
                    except Exception as e:
                        st.error(f"Could not send reset email: {auth_error_text(e)}")


# ------------------------------
# Workspace render helpers
# ------------------------------
def render_workspace_header():
    st.markdown("""
    <div class="top-header-row">
        <div class="top-header-left">
            <div class="hero-title">Kaldi One</div>
            <div class="hero-subtitle">
                AI-powered workspace for QA, BA, Development, and flow-based requirements.
            </div>
        </div>
        <div class="top-header-right">
            <a class="top-link-btn pro" href="/?view=pricing" target="_blank">⭐ Upgrade to Pro</a>
            <a class="top-link-btn support" href="mailto:kaldiglobal1008@gmail.com">Support</a>
            <a class="top-link-btn logout" href="?do_logout=1" target="_self">Logout</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_workspace_buttons():
    c1, c2, c3, c4 = st.columns(4)
    active = st.session_state.active_workspace

    with c1:
        if st.button("QA Workspace", key="btn_qa_workspace", use_container_width=True, type="primary" if active == "QA Workspace" else "secondary"):
            st.session_state.active_workspace = "QA Workspace"
            st.rerun()

    with c2:
        if st.button("BA Workspace", key="btn_ba_workspace", use_container_width=True, type="primary" if active == "BA Workspace" else "secondary"):
            st.session_state.active_workspace = "BA Workspace"
            st.rerun()

    with c3:
        if st.button("Dev Workspace", key="btn_dev_workspace", use_container_width=True, type="primary" if active == "Dev Workspace" else "secondary"):
            st.session_state.active_workspace = "Dev Workspace"
            st.rerun()

    with c4:
        if st.button("Flow to Requirement", key="btn_flow_workspace", use_container_width=True, type="primary" if active == "Flow to Requirement" else "secondary"):
            st.session_state.active_workspace = "Flow to Requirement"
            st.rerun()


def clear_generated_output_state():
    st.session_state.generated_type = None
    st.session_state.generated_title = ""
    st.session_state.generated_text = ""
    st.session_state.generated_df = None
    st.session_state.generated_base_name = ""
    st.session_state.generated_sheet_name = ""
    st.session_state.generated_mermaid_code = ""
    st.session_state.original_output_text = ""
    st.session_state.editable_output_text = ""
    st.session_state.original_output_df = None
    st.session_state.editable_output_df = None
    st.session_state.smart_review_result = None


def clear_flow_output_state():
    st.session_state.flow_generated_text = ""
    st.session_state.flow_generated_title = ""
    st.session_state.flow_generated_df = None
    st.session_state.flow_generated_base_name = ""
    st.session_state.flow_generated_mermaid_code = ""
    st.session_state.flow_original_output_text = ""
    st.session_state.flow_editable_output_text = ""
    st.session_state.flow_original_output_df = None
    st.session_state.flow_editable_output_df = None


def render_qa_workspace(user, selected_project):
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.subheader("QA Workspace")

    title = st.text_input(
        "Title",
        placeholder="Example: Login button not working on Safari mobile",
        key="qa_title_input",
    )

    context = st.text_area(
        "Requirement Details",
        height=160,
        placeholder="Paste bug details, requirement details, acceptance criteria, or observations here...",
        key="qa_context_input",
    )

    uploaded_file = st.file_uploader(
        "Upload Screenshot (Optional)",
        type=["png", "jpg", "jpeg"],
        key="qa_screenshot_upload",
    )

    output_type = st.selectbox(
        "What do you want to generate?",
        ["Bug Report", "Test Cases", "Test Scenarios"],
        key="qa_output_type_select",
    )

    is_form_valid = bool(title.strip()) and bool(context.strip())

    if not is_form_valid:
        st.info("Enter Title and Requirement Details to enable generation.")

    if st.button("Generate", disabled=not is_form_valid, key="qa_generate_btn"):
        try:
            screenshot_path = upload_screenshot_to_storage(user.id, selected_project["id"], uploaded_file) if uploaded_file else None

            with st.spinner(f"Generating {output_type}..."):
                if output_type == "Bug Report":
                    result_text, df = generate_bug_report_with_optional_image(title, context, uploaded_file)
                    sheet_name = "Bug_Report"
                    base_name = f"{safe_filename(title)}_bug_report"
                elif output_type == "Test Cases":
                    result_text, df = generate_test_cases(title, context)
                    sheet_name = "Test_Cases"
                    base_name = f"{safe_filename(title)}_test_cases"
                else:
                    result_text, df = generate_test_scenarios(title, context)
                    sheet_name = "Test_Scenarios"
                    base_name = f"{safe_filename(title)}_test_scenarios"

            set_current_output(output_type, title, result_text, df, base_name, sheet_name)

            save_item(
                user_id=user.id,
                project_id=selected_project["id"],
                item_type=output_type,
                title=title,
                input_context=context,
                output_text=result_text,
                screenshot_path=screenshot_path,
                source_filename=uploaded_file.name if uploaded_file else None,
            )

            st.success(f"{output_type} generated successfully.")

        except Exception as e:
            st.error(f"Failed to generate {output_type}: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.generated_type:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        render_current_output()
        if st.button("Clear Current Output", use_container_width=True, key="clear_qa_output"):
            clear_generated_output_state()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_ba_workspace(user, selected_project):
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.subheader("BA Workspace")

    title = st.text_input(
        "Requirement / Feature Title",
        placeholder="Example: Patient account phone number validation",
        key="ba_title_input",
    )

    context = st.text_area(
        "Business Requirement Details",
        height=180,
        placeholder="Paste the requirement, business rules, and expected behavior here...",
        key="ba_context_input",
    )

    uploaded_ba_file = st.file_uploader(
        "Upload Requirement File (Optional)",
        type=["txt", "md"],
        key="ba_requirement_upload",
    )

    output_type = st.selectbox(
        "Choose Output",
        [
            "Requirement to User Story",
            "Acceptance Criteria Generator",
            "Business Requirement Breakdown",
            "Business Process Flow",
            "Data Flow Diagram",
        ],
        key="ba_output_select",
    )

    uploaded_text = read_uploaded_text_file(uploaded_ba_file)
    full_context = context.strip()

    if uploaded_text.strip():
        if full_context:
            full_context = f"{full_context}\n\nUploaded File Content:\n{uploaded_text}"
        else:
            full_context = uploaded_text

    is_valid = bool(title.strip()) and bool(full_context.strip())

    if not is_valid:
        st.info("Enter title and requirement content, or upload a requirement file.")

    if st.button("Generate BA Output", disabled=not is_valid, key="ba_generate_btn"):
        try:
            with st.spinner(f"Generating {output_type}..."):
                if output_type in ["Business Process Flow", "Data Flow Diagram"]:
                    result_text, df, mermaid_code = generate_flow_diagram_output(title, full_context, output_type)
                else:
                    result_text, df = generate_ba_output(title, full_context, output_type)
                    mermaid_code = ""

            base_name = f"{safe_filename(title)}_{safe_filename(output_type)}"
            set_current_output(output_type, title, result_text, df, base_name, "BA_Output", mermaid_code=mermaid_code)

            save_item(
                user_id=user.id,
                project_id=selected_project["id"],
                item_type=output_type,
                title=title,
                input_context=full_context,
                output_text=result_text,
                source_filename=uploaded_ba_file.name if uploaded_ba_file else None,
            )

            st.success(f"{output_type} generated successfully.")

        except Exception as e:
            st.error(f"Failed to generate BA output: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.generated_type in [
        "Requirement to User Story",
        "Acceptance Criteria Generator",
        "Business Requirement Breakdown",
        "Business Process Flow",
        "Data Flow Diagram",
    ]:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        render_current_output()
        if st.button("Clear Current Output", use_container_width=True, key="clear_ba_output"):
            clear_generated_output_state()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_dev_workspace(user, selected_project):
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.subheader("Dev Workspace")

    title = st.text_input(
        "User Story / Requirement Title",
        placeholder="Example: Add validation for duplicate phone number",
        key="dev_title_input",
    )

    context = st.text_area(
        "Technical Context / Code",
        height=220,
        placeholder="Paste the user story, business rules, API notes, or code here...",
        key="dev_context_input",
    )

    uploaded_dev_file = st.file_uploader(
        "Upload Code File (Optional)",
        type=["py", "js", "ts", "java", "cs", "sql", "txt", "json", "md"],
        key="dev_code_upload",
    )

    language = st.selectbox(
        "Language",
        ["Auto / General", "Python", "JavaScript", "TypeScript", "Java", "C#", "SQL", "JSON", "Other"],
        key="dev_language_select",
    )

    output_type = st.selectbox(
        "Choose Output",
        [
            "Technical Task Breakdown",
            "API / Backend Tasks",
            "Developer Checklist",
            "Smart Code Review",
            "Technical Flow Diagram",
        ],
        key="dev_output_select",
    )

    uploaded_code_text = read_uploaded_text_file(uploaded_dev_file)
    full_context = context.strip()

    if uploaded_code_text.strip():
        if full_context:
            full_context = f"{full_context}\n\nUploaded File Content:\n{uploaded_code_text}"
        else:
            full_context = uploaded_code_text

    if language and language != "Auto / General":
        full_context = f"Language: {language}\n\n{full_context}"

    is_valid = bool(title.strip()) and bool(full_context.strip())

    if not is_valid:
        st.info("Enter title and technical context, or upload a code file.")

    if st.button("Generate Dev Output", disabled=not is_valid, key="dev_generate_btn"):
        try:
            with st.spinner(f"Generating {output_type}..."):
                if output_type == "Smart Code Review":
                    review_result = run_smart_code_review(full_context)
                    result_text = json.dumps(review_result, indent=2)
                    set_smart_code_review_output(title, review_result)
                    save_item(
                        user_id=user.id,
                        project_id=selected_project["id"],
                        item_type=output_type,
                        title=title,
                        input_context=full_context,
                        output_text=result_text,
                        source_filename=uploaded_dev_file.name if uploaded_dev_file else None,
                    )
                elif output_type == "Technical Flow Diagram":
                    result_text, df, mermaid_code = generate_flow_diagram_output(title, full_context, output_type)
                    base_name = f"{safe_filename(title)}_{safe_filename(output_type)}"
                    set_current_output(output_type, title, result_text, df, base_name, "Dev_Output", mermaid_code=mermaid_code)
                    save_item(
                        user_id=user.id,
                        project_id=selected_project["id"],
                        item_type=output_type,
                        title=title,
                        input_context=full_context,
                        output_text=result_text,
                        source_filename=uploaded_dev_file.name if uploaded_dev_file else None,
                    )
                else:
                    result_text, df = generate_dev_output(title, full_context, output_type)
                    base_name = f"{safe_filename(title)}_{safe_filename(output_type)}"
                    set_current_output(output_type, title, result_text, df, base_name, "Dev_Output", mermaid_code="")
                    save_item(
                        user_id=user.id,
                        project_id=selected_project["id"],
                        item_type=output_type,
                        title=title,
                        input_context=full_context,
                        output_text=result_text,
                        source_filename=uploaded_dev_file.name if uploaded_dev_file else None,
                    )

            st.success(f"{output_type} generated successfully.")

        except Exception as e:
            st.error(f"Failed to generate Dev output: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.generated_type in [
        "Technical Task Breakdown",
        "API / Backend Tasks",
        "Developer Checklist",
        "Smart Code Review",
        "Technical Flow Diagram",
    ]:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        render_current_output()
        if st.button("Clear Current Output", use_container_width=True, key="clear_dev_output"):
            clear_generated_output_state()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_flow_workspace():
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.subheader("Flow to Requirement")

    uploaded_flow = st.file_uploader(
        "Upload Flow Diagram",
        type=["png", "jpg", "jpeg", "pdf"],
        key="flow_diagram_upload",
    )

    if uploaded_flow is not None:
        reset_flow_output_if_new_file(uploaded_flow)

        if uploaded_flow.type in ["image/png", "image/jpg", "image/jpeg"]:
            st.image(uploaded_flow, caption="Uploaded Flow Diagram", use_container_width=True)
        elif uploaded_flow.type == "application/pdf":
            st.info(f"PDF uploaded: {uploaded_flow.name}")

    flow_btn = st.button(
        "Generate Requirements",
        disabled=uploaded_flow is None,
        key="generate_flow_requirements",
    )

    if uploaded_flow is None:
        st.info("Upload a flow diagram to enable Generate Requirements.")

    if flow_btn and uploaded_flow is not None:
        try:
            flow_title = uploaded_flow.name.rsplit(".", 1)[0]

            with st.spinner("Generating requirements from flow..."):
                result_text, df_flow = generate_requirements_from_flow(uploaded_flow)

            flow_edit_df = df_flow.copy()
            if "Select" not in flow_edit_df.columns:
                flow_edit_df.insert(0, "Select", False)

            st.session_state.flow_generated_title = flow_title
            st.session_state.flow_generated_text = result_text
            st.session_state.flow_generated_df = df_flow
            st.session_state.flow_generated_base_name = f"{safe_filename(flow_title)}_requirements"
            st.session_state.flow_generated_mermaid_code = ""
            st.session_state.flow_original_output_text = result_text
            st.session_state.flow_editable_output_text = result_text
            st.session_state.flow_original_output_df = df_flow.copy()
            st.session_state.flow_editable_output_df = flow_edit_df

            st.success("Requirements generated successfully.")

        except Exception as e:
            st.error(f"Failed to generate requirements from flow: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.flow_generated_df is not None:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        render_flow_output()

        if st.button("Clear Flow Output", use_container_width=True, key="clear_flow_output"):
            clear_flow_output_state()
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------
# Main app UI
# ------------------------------
def render_main_app():
    user = st.session_state.user
    if not user:
        render_auth_screen()
        return

    _, selected_project, _ = render_sidebar_projects(user)

    if not selected_project:
        st.warning("Please create or select a project first.")
        return

    render_workspace_header()
    render_workspace_buttons()

    workspace = st.session_state.active_workspace

    if workspace == "QA Workspace":
        render_qa_workspace(user, selected_project)
    elif workspace == "BA Workspace":
        render_ba_workspace(user, selected_project)
    elif workspace == "Dev Workspace":
        render_dev_workspace(user, selected_project)
    elif workspace == "Flow to Requirement":
        render_flow_workspace()


# ------------------------------
# Boot existing auth session once
# ------------------------------
if not st.session_state.auth_checked:
    load_user_from_existing_session()
    st.session_state.auth_checked = True


# ------------------------------
# Handle logout from header link
# ------------------------------
if st.query_params.get("do_logout") == "1":
    sign_out_user()
    st.query_params.clear()
    st.rerun()


# ------------------------------
# Run app
# ------------------------------
render_main_app()
