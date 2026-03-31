import streamlit as st

st.set_page_config(page_title="Kaldi AI QA Assistant", page_icon="🚀", layout="wide")

st.title("👋 Welcome to Kaldi QA")
st.caption("AI-powered QA workflow for faster testing, smarter bug reporting, and organized project execution.")

st.markdown("## Generate QA outputs faster")
st.write(
    "Create bug reports, test cases, test scenarios, and flow-based requirements in one place. "
    "Organize your work by project and streamline execution with Jira integration."
)

c1, c2 = st.columns(2)

with c1:
    st.markdown("### What you can do")
    st.markdown(
        """
        - Generate bug reports from text or screenshots
        - Generate structured test cases
        - Generate high-level test scenarios
        - Convert flow diagrams into requirements
        - Save outputs by project
        - Connect Jira for issue creation
        """
    )

with c2:
    st.markdown("### Who it is for")
    st.markdown(
        """
        - QA analysts
        - Test engineers
        - QA consultants
        - Small product teams
        - Teams that want faster documentation and better workflow
        """
    )

st.markdown("---")

st.markdown("## How it works")

h1, h2, h3 = st.columns(3)

with h1:
    st.info("**1. Enter context**\n\nAdd requirement details, issue details, or upload a screenshot or flow.")

with h2:
    st.info("**2. Generate output**\n\nCreate AI-assisted bug reports, test cases, scenarios, or requirements.")

with h3:
    st.info("**3. Save and manage**\n\nStore outputs by project and move work into Jira when needed.")

st.markdown("---")

st.markdown("## Key Features")

f1, f2, f3 = st.columns(3)
with f1:
    st.success("Bug Report Generation")
with f2:
    st.success("Test Case Generation")
with f3:
    st.success("Jira Integration")

f4, f5, f6 = st.columns(3)
with f4:
    st.success("Project-Based Organization")
with f5:
    st.success("Flow to Requirements")
with f6:
    st.success("Download to TXT / CSV / Excel")

st.markdown("---")

st.markdown("## Pricing Overview")

p1, p2 = st.columns(2)

with p1:
    st.markdown(
        """
        ### Free
        - 1 project
        - Core QA generation
        - Basic workflow
        """
    )

with p2:
    st.markdown(
        """
        ### Pro
        - Unlimited projects
        - Jira integration
        - Premium workflow features
        """
    )

st.markdown("---")

st.markdown("## Get Started")

a1, a2, a3 = st.columns(3)

with a1:
    st.page_link("pages/1_Login_and_Start.py", label="Login and Start", icon="🧪")

with a2:
    st.page_link("pages/4_Pricing.py", label="View Pricing", icon="💳")

with a3:
    st.page_link("pages/5_Contact_Support.py", label="Contact Support", icon="📩")

st.markdown("---")

l1, l2 = st.columns(2)

with l1:
    st.page_link("pages/6_Privacy_Policy.py", label="Privacy Policy", icon="🔒")

with l2:
    st.page_link("pages/7_Terms_of_Service.py", label="Terms of Service", icon="📄")
