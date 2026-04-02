import os
from urllib.parse import unquote

import pandas as pd
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
    page_title="History",
    page_icon="🕘",
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

# ------------------------------
# Styling
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
    font-size: 2.2rem;
    font-weight: 700;
    color: #1f2937;
    margin-top: 0;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

.hero-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.2rem;
}

.clean-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
}

.history-pill {
    display: inline-block;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    background: #eff6ff;
    border: 1px solid #dbeafe;
    color: #1d4ed8;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.history-meta {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 0.2rem;
}

.empty-card {
    border: 1px dashed #cbd5e1;
    border-radius: 18px;
    background: #f8fafc;
    padding: 1.4rem;
    color: #475569;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# DB helpers
# ------------------------------
def get_projects(user_id: str):
    resp = (
        supabase.table("projects")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return resp.data or []


def get_recent_items(user_id: str, limit: int = 100):
    resp = (
        supabase.table("saved_items")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


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


def delete_project_item(user_id: str, item_id: str):
    item_resp = (
        supabase.table("saved_items")
        .select("id,screenshot_path")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = item_resp.data or []
    if not rows:
        return

    screenshot_path = rows[0].get("screenshot_path")
    if screenshot_path:
        try:
            supabase.storage.from_("screenshots").remove([screenshot_path])
        except Exception:
            pass

    supabase.table("saved_items").delete().eq("id", item_id).eq("user_id", user_id).execute()


def get_signed_screenshot_url(storage_path: str, expires_in: int = 3600):
    if not storage_path:
        return None
    try:
        res = supabase.storage.from_("screenshots").create_signed_url(storage_path, expires_in)
        if isinstance(res, dict):
            return res.get("signedURL") or res.get("signedUrl")
        return None
    except Exception:
        return None


def item_matches_search(item, search_term: str):
    if not search_term:
        return True

    term = search_term.lower().strip()
    haystack = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("item_type", "")),
            str(item.get("output_text", ""))[:2500],
            str(item.get("source_filename", "")),
            str(item.get("input_context", ""))[:1500],
        ]
    ).lower()

    return term in haystack


def get_item_df(item):
    item_type = item.get("item_type", "")
    output_text = item.get("output_text", "")

    try:
        if item_type == "Bug Report":
            data = {}
            for line in output_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()
            return pd.DataFrame([data]) if data else pd.DataFrame([{"Output": output_text}])

        return pd.DataFrame([{"Output": output_text}])
    except Exception:
        return pd.DataFrame([{"Output": output_text}])


# ------------------------------
# Page
# ------------------------------
st.markdown('<div class="hero-title">History</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">View and manage your recent generated items by project.</div>',
    unsafe_allow_html=True,
)

projects = get_projects(user.id)

project_options = ["All Projects"] + [p["name"] for p in projects]
selected_project_name = st.selectbox("Filter by Project", project_options)

search_term = st.text_input(
    "Search history",
    placeholder="Search by title, item type, or output text...",
)

if selected_project_name == "All Projects":
    items = get_recent_items(user.id, limit=100)
else:
    selected_project = next((p for p in projects if p["name"] == selected_project_name), None)
    items = get_project_items(user.id, selected_project["id"]) if selected_project else []

filtered_items = [item for item in items if item_matches_search(item, search_term)]

if not filtered_items:
    st.markdown("""
    <div class="empty-card">
        No history found yet. Generate bug reports, test cases, BA outputs, or Dev outputs to see them here.
    </div>
    """, unsafe_allow_html=True)
else:
    for item in filtered_items:
        title = item.get("title", "Untitled")
        item_type = item.get("item_type", "Output")
        created_at = item.get("created_at", "")
        source_filename = item.get("source_filename", "")
        output_text = item.get("output_text", "")

        st.markdown('<div class="clean-card">', unsafe_allow_html=True)

        st.markdown(f'<div class="history-pill">{item_type}</div>', unsafe_allow_html=True)
        st.subheader(title)

        meta_parts = []
        if created_at:
            meta_parts.append(f"Created: {created_at}")
        if source_filename:
            meta_parts.append(f"File: {source_filename}")

        if meta_parts:
            st.markdown(
                f'<div class="history-meta">{" • ".join(meta_parts)}</div>',
                unsafe_allow_html=True,
            )

        screenshot_path = item.get("screenshot_path")
        if screenshot_path:
            signed_url = get_signed_screenshot_url(screenshot_path)
            if signed_url:
                st.image(signed_url, caption="Saved Screenshot", use_container_width=True)

        df = get_item_df(item)
        st.dataframe(df, use_container_width=True)

        with st.expander("View Full Output", expanded=False):
            st.text_area(
                "Output",
                value=output_text,
                height=240,
                key=f"history_output_{item['id']}",
            )

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "Download TXT",
                data=output_text,
                file_name=f"{title.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"download_history_{item['id']}",
            )

        with c2:
            if st.button("Delete", use_container_width=True, key=f"delete_history_{item['id']}"):
                delete_project_item(user.id, item["id"])
                st.success("History item deleted.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)