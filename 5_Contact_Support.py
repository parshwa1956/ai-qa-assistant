import streamlit as st

st.set_page_config(page_title="Contact & Support", page_icon="📩", layout="wide")

st.title("📩 Contact & Support")
st.caption("Need help? Send us your question or feedback.")

st.markdown("## Support Information")
st.write("For now, you can reach support at:")
st.info("kaldiglobal1008@gmail.com")

st.markdown("## Send a Message")

with st.form("support_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    subject = st.text_input("Subject")
    message = st.text_area("Message", height=180)

    submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip() or not subject.strip() or not message.strip():
            st.error("Please complete all fields.")
        else:
            st.success("Your message has been captured. Email/Supabase integration can be connected next.")

st.markdown("## Frequently Asked Support Topics")

with st.expander("How do I upgrade to Pro?"):
    st.write("Upgrade flow will be connected through Stripe in the next phase.")

with st.expander("How do I connect Jira?"):
    st.write("You can connect Jira from the main app in the Jira settings section.")

with st.expander("How do I reset my password?"):
    st.write("Use Forgot Password on the login page.")