import os
from urllib.parse import unquote
from datetime import datetime, timezone

import requests
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# ------------------------------
# Load environment
# ------------------------------
load_dotenv()

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

# ------------------------------
# Helpers
# ------------------------------
def get_secret_or_env(name: str, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


SUPABASE_URL = get_secret_or_env("SUPABASE_URL")
SUPABASE_KEY = get_secret_or_env("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL or SUPABASE_KEY not found in Streamlit secrets or .env.")
    st.stop()


@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = get_supabase()

# ------------------------------
# Session restore
# ------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "auth_checked" not in st.session_state:
    st.session_state.auth_checked = False


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


if not st.session_state.auth_checked:
    load_user_from_existing_session()
    st.session_state.auth_checked = True

user = st.session_state.user

if not user:
    st.error("Please log in first from the Login and Start page.")
    st.stop()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


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


def save_jira_integration(
    user_id: str,
    jira_base_url: str,
    jira_email: str,
    jira_api_token: str,
    jira_project_key: str,
):
    payload = {
        "user_id": user_id,
        "jira_base_url": jira_base_url.strip().rstrip("/"),
        "jira_email": jira_email.strip(),
        "jira_api_token": jira_api_token.strip(),
        "jira_project_key": jira_project_key.strip().upper(),
        "updated_at": now_iso(),
    }

    existing = get_jira_integration(user_id)

    if existing:
        return (
            supabase.table("jira_integrations")
            .update(payload)
            .eq("user_id", user_id)
            .execute()
        )

    payload["created_at"] = now_iso()
    return supabase.table("jira_integrations").insert(payload).execute()


def delete_jira_integration(user_id: str):
    return (
        supabase.table("jira_integrations")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )


def test_jira_connection(jira_base_url, jira_email, jira_api_token):
    if not all([jira_base_url, jira_email, jira_api_token]):
        return False, "Please complete Jira Base URL, Jira Email, and Jira API Token."

    url = f"{jira_base_url.rstrip('/')}/rest/api/3/myself"
    headers = {"Accept": "application/json"}
    auth = (jira_email, jira_api_token)

    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
    except Exception as e:
        return False, f"Connection failed: {e}"

    if response.status_code == 200:
        data = response.json()
        display_name = data.get("displayName", "Connected user")
        return True, f"Connected successfully as {display_name}"

    return False, response.text


def update_logged_in_user_password(new_password: str):
    return supabase.auth.update_user({"password": new_password})


# ------------------------------
# Styling
# ------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 980px;
    margin: 0 auto;
    padding-top: 3.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.hero-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.25rem;
}

.clean-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
}

.integration-badge {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #dbeafe;
    font-size: 0.84rem;
    font-weight: 600;
    margin-bottom: 0.65rem;
}

.muted {
    color: #6b7280;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

jira_config = get_jira_integration(user.id)

default_jira_url = jira_config["jira_base_url"] if jira_config else ""
default_jira_email = jira_config["jira_email"] if jira_config else ""
default_jira_project_key = jira_config["jira_project_key"] if jira_config else ""

# ------------------------------
# Header
# ------------------------------
st.markdown('<div class="hero-title">Settings</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Connect external tools and manage your account preferences.</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Integrations", "Account"])

# ------------------------------
# Integrations
# ------------------------------
with tab1:
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown('<div class="integration-badge">Primary Integration</div>', unsafe_allow_html=True)
    st.subheader("JIRA")
    st.markdown(
        '<div class="muted">Connect JIRA to create issues directly from generated QA output.</div>',
        unsafe_allow_html=True,
    )

    jira_base_url = st.text_input(
        "JIRA Base URL",
        value=default_jira_url,
        placeholder="https://your-company.atlassian.net",
    )

    jira_email = st.text_input(
        "JIRA Email",
        value=default_jira_email,
        placeholder="you@company.com",
    )

    jira_api_token = st.text_input(
        "JIRA API Token",
        type="password",
        placeholder="Paste your JIRA API token",
    )

    jira_project_key = st.text_input(
        "JIRA Project Key",
        value=default_jira_project_key,
        placeholder="QA",
    )

    if jira_config:
        st.success(
            f"Connected configuration found: {jira_config.get('jira_base_url')} / {jira_config.get('jira_project_key')}"
        )
    else:
        st.info("No JIRA configuration saved yet.")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Test JIRA Connection", use_container_width=True):
            token_to_use = jira_api_token.strip() if jira_api_token.strip() else (
                jira_config["jira_api_token"] if jira_config else ""
            )

            ok, msg = test_jira_connection(
                jira_base_url.strip(),
                jira_email.strip(),
                token_to_use,
            )
            if ok:
                st.success(msg)
            else:
                st.error(f"Test failed: {msg}")

    with c2:
        if st.button("Save JIRA Settings", use_container_width=True):
            token_to_save = jira_api_token.strip() if jira_api_token.strip() else (
                jira_config["jira_api_token"] if jira_config else ""
            )

            if not jira_base_url.strip() or not jira_email.strip() or not token_to_save or not jira_project_key.strip():
                st.error("Please complete all JIRA fields before saving.")
            else:
                try:
                    save_jira_integration(
                        user_id=user.id,
                        jira_base_url=jira_base_url,
                        jira_email=jira_email,
                        jira_api_token=token_to_save,
                        jira_project_key=jira_project_key,
                    )
                    st.success("JIRA settings saved successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save JIRA settings: {e}")

    with c3:
        if st.button("Remove JIRA", use_container_width=True):
            try:
                delete_jira_integration(user.id)
                st.success("JIRA settings removed.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to remove JIRA settings: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown('<div class="integration-badge">Coming Next</div>', unsafe_allow_html=True)
    st.subheader("Azure DevOps")
    st.markdown(
        '<div class="muted">Prepare Azure DevOps integration so users can create work items directly from generated output.</div>',
        unsafe_allow_html=True,
    )

    st.text_input(
        "Organization URL",
        placeholder="https://dev.azure.com/your-org",
        key="ado_org_url",
    )
    st.text_input(
        "Project Name",
        placeholder="Example: Kaldi QA",
        key="ado_project_name",
    )
    st.text_input(
        "Personal Access Token",
        type="password",
        placeholder="Paste Azure DevOps PAT",
        key="ado_pat",
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Test Azure DevOps Connection", use_container_width=True):
            st.info("Azure DevOps test connection can be wired next.")

    with c2:
        if st.button("Save Azure DevOps Settings", use_container_width=True):
            st.info("Azure DevOps save logic can be added next.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# Account
# ------------------------------
with tab2:
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.subheader("Account")
    st.write(f"Logged in as: **{user.email}**")

    with st.expander("Change Password", expanded=False):
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")

        if st.button("Update Password", use_container_width=True):
            if not new_password.strip():
                st.error("Please enter a new password.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    update_logged_in_user_password(new_password.strip())
                    st.success("Password updated successfully.")
                except Exception as e:
                    st.error(f"Password update failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)