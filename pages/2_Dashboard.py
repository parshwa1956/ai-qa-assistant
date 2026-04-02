import os
from urllib.parse import unquote
from datetime import datetime, timezone

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
    page_title="Dashboard",
    page_icon="📊",
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
# Data helpers
# ------------------------------
def get_projects(user_id: str):
    try:
        resp = (
            supabase.table("projects")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def get_saved_items(user_id: str):
    try:
        resp = (
            supabase.table("saved_items")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


projects = get_projects(user.id)
items = get_saved_items(user.id)

test_cases = [x for x in items if x.get("item_type") == "Test Cases"]
bugs = [x for x in items if x.get("item_type") == "Bug Report"]
recent_projects = projects[:5]
recent_test_cases = test_cases[:5]
recent_bugs = bugs[:5]

# ------------------------------
# Styling
# ------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1180px;
    margin: 0 auto;
    padding-top: 3.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f2937;
    margin-top: 0.15rem;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.hero-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #1f2937;
    margin-top: 1rem;
    margin-bottom: 0.85rem;
}

.clean-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
}

.stat-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
    min-height: 128px;
}

.stat-label {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 0.55rem;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
}

.stat-note {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 0.45rem;
}

.action-card {
    border: 1px solid #dbeafe;
    border-radius: 16px;
    background: #f8fbff;
    padding: 1rem;
    min-height: 92px;
}

.action-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e3a8a;
    margin-bottom: 0.35rem;
}

.action-text {
    color: #64748b;
    font-size: 0.92rem;
}

.list-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
    min-height: 250px;
}

.list-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.85rem;
}

.list-item {
    border: 1px solid #eef2f7;
    background: #f8fafc;
    border-radius: 12px;
    padding: 0.8rem 0.9rem;
    margin-bottom: 0.65rem;
}

.list-item-title {
    font-size: 0.98rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.2rem;
}

.list-item-meta {
    color: #64748b;
    font-size: 0.85rem;
}

.next-step-card {
    border: 1px solid #d1fae5;
    border-radius: 18px;
    background: #ecfdf5;
    padding: 1rem 1.1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.02);
}

.next-step-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #065f46;
    margin-bottom: 0.25rem;
}

.next-step-text {
    color: #047857;
    font-size: 0.94rem;
}

div.stButton > button {
    border-radius: 12px;
    height: 44px;
}

.refresh-wrap {
    padding-top: 1.25rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Header
# ------------------------------
col1, col2 = st.columns([4, 1.3])

with col1:
    st.markdown('<div class="hero-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Welcome to Kaldi One AI Assistant</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="refresh-wrap">', unsafe_allow_html=True)
    if st.button("Refresh Dashboard", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="clean-card"><span style="font-size:1.7rem;font-weight:700;color:#1f2937;">Welcome back, </span>'
    f'<span style="font-size:1.7rem;font-weight:700;color:#2563eb;">{user.email}</span></div>',
    unsafe_allow_html=True,
)

# ------------------------------
# Overview
# ------------------------------
st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Projects</div>
        <div class="stat-value">{len(projects)}</div>
        <div class="stat-note">Projects created in your workspace</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Test Cases</div>
        <div class="stat-value">{len(test_cases)}</div>
        <div class="stat-note">Generated QA test cases</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Bugs</div>
        <div class="stat-value">{len(bugs)}</div>
        <div class="stat-note">Bug reports saved in history</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Quick actions
# ------------------------------
st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">Create Project</div>
        <div class="action-text">Create your first project from the main app sidebar to organize QA work.</div>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">Generate Test Cases</div>
        <div class="action-text">Use the QA workspace to generate clean and structured test cases quickly.</div>
    </div>
    """, unsafe_allow_html=True)

with a3:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">Generate Bug Reports</div>
        <div class="action-text">Turn requirements or screenshots into professional bug reports in seconds.</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Recent activity
# ------------------------------
st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown('<div class="list-card"><div class="list-title">Recent Projects</div>', unsafe_allow_html=True)
    if recent_projects:
        for item in recent_projects:
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-title">{item.get("name", "Untitled Project")}</div>
                <div class="list-item-meta">Project workspace</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="list-item">
            <div class="list-item-title">No projects yet</div>
            <div class="list-item-meta">Create one from the main app sidebar</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2:
    st.markdown('<div class="list-card"><div class="list-title">Recent Test Cases</div>', unsafe_allow_html=True)
    if recent_test_cases:
        for item in recent_test_cases:
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-title">{item.get("title", "Untitled Test Case")}</div>
                <div class="list-item-meta">Generated test case</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="list-item">
            <div class="list-item-title">No test cases yet</div>
            <div class="list-item-meta">Generate from the QA workspace</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r3:
    st.markdown('<div class="list-card"><div class="list-title">Recent Bugs</div>', unsafe_allow_html=True)
    if recent_bugs:
        for item in recent_bugs:
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-title">{item.get("title", "Untitled Bug")}</div>
                <div class="list-item-meta">Saved bug report</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="list-item">
            <div class="list-item-title">No bug reports yet</div>
            <div class="list-item-meta">Generate from the QA workspace</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Next step
# ------------------------------
st.markdown('<div class="section-title">Next Step</div>', unsafe_allow_html=True)
st.markdown("""
<div class="next-step-card">
    <div class="next-step-title">Start building your workspace</div>
    <div class="next-step-text">
        Create a project first, then generate test cases, bug reports, or test scenarios from the main app.
    </div>
</div>
""", unsafe_allow_html=True)