import streamlit as st
from supabase import create_client, Client

# =========================
# CONFIG
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Profile & Settings", page_icon="⚙️", layout="wide")


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


def get_profile(user_id):
    try:
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None
    except Exception as e:
        st.error(f"Could not load profile: {e}")
        return None


def save_profile(user_id, email, full_name, company_name, plan_name):
    try:
        payload = {
            "id": user_id,
            "email": email,
            "full_name": full_name.strip(),
            "company_name": company_name.strip(),
            "plan_name": plan_name.strip() if plan_name else "Free",
        }

        return supabase.table("profiles").upsert(payload).execute()
    except Exception as e:
        st.error(f"Could not save profile: {e}")
        return None


def get_jira_integration(user_id):
    try:
        response = (
            supabase.table("jira_integrations")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None
    except Exception as e:
        st.warning(f"Could not load Jira status: {e}")
        return None


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
profile = get_profile(user_id)
jira_config = get_jira_integration(user_id)

full_name_default = profile.get("full_name", "") if profile else ""
company_name_default = profile.get("company_name", "") if profile else ""
plan_name_default = profile.get("plan_name", "Free") if profile else "Free"


# =========================
# PAGE HEADER
# =========================
st.title("⚙️ Profile & Settings")
st.caption("Manage your account details and connected tools")

left, right = st.columns([2, 1])

with left:
    st.subheader("Account Information")
    st.write(f"**Email:** {user_email}")

with right:
    if jira_config:
        st.success("Jira Connected")
    else:
        st.warning("Jira Not Connected")


# =========================
# PROFILE FORM
# =========================
st.markdown("## Profile Details")

with st.form("profile_settings_form"):
    full_name = st.text_input("Full Name", value=full_name_default)
    company_name = st.text_input("Company Name", value=company_name_default)
    plan_name = st.selectbox(
        "Current Plan",
        options=["Free", "Pro"],
        index=0 if plan_name_default == "Free" else 1,
    )

    submitted = st.form_submit_button("Save Profile", use_container_width=True)

    if submitted:
        save_profile(
            user_id=user_id,
            email=user_email,
            full_name=full_name,
            company_name=company_name,
            plan_name=plan_name,
        )
        st.success("Profile updated successfully.")
        st.rerun()


# =========================
# ACCOUNT SUMMARY
# =========================
st.markdown("## Account Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.info(f"**Email**\n\n{user_email}")

with c2:
    st.info(f"**Plan**\n\n{plan_name_default}")

with c3:
    st.info(f"**Jira Status**\n\n{'Connected' if jira_config else 'Not Connected'}")


# =========================
# JIRA STATUS
# =========================
st.markdown("## Jira Connection")

if jira_config:
    st.success("Your Jira integration is active.")
    st.write(f"**Base URL:** {jira_config.get('jira_base_url', '-')}")
    st.write(f"**Jira Email:** {jira_config.get('jira_email', '-')}")
    st.write(f"**Project Key:** {jira_config.get('jira_project_key', '-')}")
else:
    st.info("Jira is not connected yet. Connect it from the main app Jira section.")


# =========================
# SECURITY NOTE
# =========================
st.markdown("## Security")
st.caption("Password changes are currently handled from the login page using Forgot Password or Set New Password.")