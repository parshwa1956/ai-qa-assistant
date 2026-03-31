import streamlit as st
from supabase import create_client, Client

# =========================
# CONFIG
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Subscription", page_icon="💼", layout="wide")


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


def update_plan(user_id, email, full_name, company_name, plan_name):
    try:
        payload = {
            "id": user_id,
            "email": email,
            "full_name": full_name or "",
            "company_name": company_name or "",
            "plan_name": plan_name,
        }
        supabase.table("profiles").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Could not update subscription plan: {e}")
        return False


st.title("💼 Subscription")
st.caption("Manage your current plan")

user = get_logged_in_user()

if not user:
    st.warning("Please log in first.")
    st.stop()

user_id = get_user_id()
user_email = get_user_email()

profile = get_profile(user_id)
full_name = profile.get("full_name", "") if profile else ""
company_name = profile.get("company_name", "") if profile else ""
current_plan = profile.get("plan_name", "Free") if profile else "Free"

st.markdown("## Current Subscription")
st.info(f"Logged in as: {user_email}")
st.success(f"Current Plan: {current_plan}")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
        ### Free
        **$0 / month**

        - 1 project
        - Generate bug reports
        - Generate test cases
        - Generate test scenarios
        - Basic usage
        """
    )

    if current_plan == "Free":
        st.button("Current Plan", use_container_width=True, disabled=True)
    else:
        if st.button("Switch to Free", use_container_width=True):
            if update_plan(user_id, user_email, full_name, company_name, "Free"):
                st.success("Plan updated to Free.")
                st.rerun()

with c2:
    st.markdown(
        """
        ### Pro
        **$19 / month**

        - Unlimited projects
        - Jira integration
        - Better workflow
        - Priority support
        - Future premium AI features
        """
    )

    if current_plan == "Pro":
        st.button("Current Plan", use_container_width=True, disabled=True)
    else:
        if st.button("Upgrade to Pro", use_container_width=True):
            if update_plan(user_id, user_email, full_name, company_name, "Pro"):
                st.success("Plan updated to Pro.")
                st.rerun()

st.markdown("---")
st.warning("This is a local/manual subscription flow for testing. Stripe checkout can be connected next.")