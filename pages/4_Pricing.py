import streamlit as st

st.set_page_config(page_title="Pricing", page_icon="💳", layout="wide")

st.title("💳 Pricing")
st.caption("Simple pricing for Kaldi AI QA Assistant")

st.markdown("## Choose the plan that fits your QA workflow")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### Free

        **$0 / month**

        - 1 project
        - Generate bug reports
        - Generate test cases
        - Generate test scenarios
        - Basic usage
        - Standard support
        """
    )

    st.button("Current Free Plan", use_container_width=True, disabled=True)

with col2:
    st.markdown(
        """
        ### Pro

        **$19 / month**

        - Unlimited projects
        - Jira integration
        - Better workflow for teams
        - Priority support
        - Future premium AI features
        """
    )

    if st.button("Upgrade to Pro", use_container_width=True):
        st.info("Stripe checkout will be connected in the next step.")

st.markdown("---")

st.markdown("## Why upgrade?")
st.write(
    "Pro is designed for QA professionals, consultants, and teams who want a more organized workflow, "
    "better project management, and Jira-connected execution."
)

st.markdown("## Frequently Asked Questions")

with st.expander("Can I start with the Free plan?"):
    st.write("Yes. You can use the Free plan to explore the product and validate your workflow.")

with st.expander("When will billing be connected?"):
    st.write("Billing and subscription checkout will be connected in the next phase using Stripe.")

with st.expander("Will more AI features come later?"):
    st.write("Yes. Future versions can include smarter QA automation, reporting, and enhanced integrations.")