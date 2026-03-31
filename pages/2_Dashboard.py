import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# =========================
# CONFIG
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")


# =========================
# HELPERS
# =========================
def get_logged_in_user():
    return st.session_state.get("user", None)


def get_user_id():
    user = get_logged_in_user()
    if not user:
        return None

    if isinstance(user, dict):
        return user.get("id")
    return getattr(user, "id", None)


def get_user_email():
    user = get_logged_in_user()
    if not user:
        return ""

    if isinstance(user, dict):
        return user.get("email", "")
    return getattr(user, "email", "")


def format_datetime(dt_string):
    if not dt_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return dt_string


def safe_project_count(user_id):
    try:
        response = (
            supabase.table("projects")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return response.count if response.count is not None else 0
    except Exception as e:
        st.warning(f"Could not load project count: {e}")
        return 0


def safe_saved_item_count(user_id, item_type=None):
    try:
        query = (
            supabase.table("saved_items")
            .select("id", count="exact")
            .eq("user_id", user_id)
        )

        if item_type:
            query = query.eq("item_type", item_type)

        response = query.execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        st.warning(f"Could not load saved item count: {e}")
        return 0


def get_recent_projects(user_id, limit=5):
    try:
        response = (
            supabase.table("projects")
            .select("id, name, created_at, updated_at")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        st.warning(f"Could not load recent projects: {e}")
        return []


def get_recent_saved_items(user_id, item_type=None, limit=5):
    try:
        query = (
            supabase.table("saved_items")
            .select("id, title, item_type, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )

        if item_type:
            query = query.eq("item_type", item_type)

        response = query.execute()
        return response.data or []
    except Exception as e:
        st.warning(f"Could not load recent items: {e}")
        return []


# =========================
# AUTH CHECK
# =========================
user = get_logged_in_user()

if not user:
    st.warning("Please log in first.")
    st.stop()

user_id = get_user_id()
user_email = get_user_email()

if not user_id:
    st.error("User session found, but user ID is missing.")
    st.stop()


# =========================
# LOAD DATA
# =========================
project_count = safe_project_count(user_id)
test_case_count = safe_saved_item_count(user_id, "Test Cases")
bug_count = safe_saved_item_count(user_id, "Bug Report")

recent_projects = get_recent_projects(user_id)
recent_test_cases = get_recent_saved_items(user_id, "Test Cases")
recent_bugs = get_recent_saved_items(user_id, "Bug Report")


# =========================
# HEADER
# =========================
st.title("📊 Dashboard")
st.caption("Welcome to Kaldi AI QA Assistant")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"Welcome back, {user_email}")

with col2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()


# =========================
# METRICS
# =========================
st.markdown("## Overview")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(label="Total Projects", value=project_count)

with m2:
    st.metric(label="Total Test Cases", value=test_case_count)

with m3:
    st.metric(label="Total Bugs", value=bug_count)


# =========================
# QUICK ACTIONS
# =========================
st.markdown("## Quick Actions")

q1, q2, q3 = st.columns(3)

with q1:
    st.info("Create Project from the main app sidebar")

with q2:
    st.info("Generate Test Cases from the main app")

with q3:
    st.info("Generate Bug Reports from the main app")


# =========================
# RECENT ACTIVITY
# =========================
st.markdown("## Recent Activity")

left, middle, right = st.columns(3)

with left:
    st.markdown("### Recent Projects")
    if recent_projects:
        for item in recent_projects:
            st.markdown(
                f"""
                **{item.get('name', 'Untitled Project')}**  
                Created: {format_datetime(item.get('created_at'))}  
                Updated: {format_datetime(item.get('updated_at'))}
                """
            )
            st.divider()
    else:
        st.info("No projects yet.")

with middle:
    st.markdown("### Recent Test Cases")
    if recent_test_cases:
        for item in recent_test_cases:
            st.markdown(
                f"""
                **{item.get('title', 'Untitled Test Case')}**  
                Type: {item.get('item_type', '')}  
                Created: {format_datetime(item.get('created_at'))}
                """
            )
            st.divider()
    else:
        st.info("No test cases yet.")

with right:
    st.markdown("### Recent Bugs")
    if recent_bugs:
        for item in recent_bugs:
            st.markdown(
                f"""
                **{item.get('title', 'Untitled Bug')}**  
                Type: {item.get('item_type', '')}  
                Created: {format_datetime(item.get('created_at'))}
                """
            )
            st.divider()
    else:
        st.info("No bug reports yet.")


# =========================
# NEXT STEP
# =========================
st.markdown("## Next Step")

if project_count == 0:
    st.success("Create your first project from the sidebar in the main app.")
elif test_case_count == 0:
    st.success("Great start. Now generate your first test case.")
elif bug_count == 0:
    st.success("Nice progress. Now generate your first bug report.")
else:
    st.success("Your QA workspace is active and ready to grow.")