import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# ------------------------------
# Load environment
# ------------------------------
load_dotenv()

api_key = None
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Add it in Streamlit Secrets or local .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="AI QA Assistant",
    page_icon="🧪",
    layout="centered",
)

# ------------------------------
# Header
# ------------------------------
st.title("AI QA Assistant")
st.write("Generate bug reports, test cases, and high-level test scenarios using AI.")

# ------------------------------
# Inputs
# ------------------------------
title = st.text_input(
    "Title / Requirement / Feature *",
    placeholder="Example: Patient should be able to reschedule appointments online"
)

context = st.text_area(
    "Context / Business Requirement Details *",
    height=150,
    placeholder="Paste the business requirement, bug details, acceptance criteria, or feature context here..."
)

uploaded_file = st.file_uploader(
    "Upload Screenshot (Optional)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)

# ------------------------------
# Validation
# ------------------------------
is_form_valid = bool(title.strip()) and bool(context.strip())

if is_form_valid:
    st.success("Looks good. You can now generate outputs.")
else:
    st.info("Please enter both Title and Context to enable all actions.")

# ------------------------------
# Buttons
# ------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    bug_btn = st.button("Generate Bug Report", disabled=not is_form_valid, use_container_width=True)

with col2:
    case_btn = st.button("Generate Test Cases", disabled=not is_form_valid, use_container_width=True)

with col3:
    scenario_btn = st.button("Generate Test Scenarios", disabled=not is_form_valid, use_container_width=True)

# ------------------------------
# Generate Bug Report
# ------------------------------
if bug_btn:
    screenshot_note = "A screenshot was uploaded and should be considered if relevant." if uploaded_file else "No screenshot uploaded."

    prompt = f"""
You are a senior QA engineer.

Generate a professional bug report for the following issue.

Title / Requirement / Feature: {title}
Context: {context}
Screenshot Note: {screenshot_note}

Return the output with these sections:
Title
Description
Steps to Reproduce
Expected Result
Actual Result
Severity
Environment

Keep it practical, realistic, and ready to copy into Jira or Azure DevOps.
If some details are missing, make reasonable QA assumptions.
"""

    with st.spinner("Generating bug report..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

    st.subheader("Generated Bug Report")
    st.write(response.choices[0].message.content)

# ------------------------------
# Generate Test Cases
# ------------------------------
if case_btn:
    prompt = f"""
You are a senior QA engineer.

Generate detailed QA test cases for the following issue, feature, or requirement.

Title / Requirement / Feature: {title}
Context: {context}

Return the output with these sections:
Functional Test Cases
Negative Test Cases
Edge Cases
Regression Test Cases

Keep the test cases practical, concise, and useful for QA execution.
"""

    with st.spinner("Generating test cases..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

    st.subheader("Generated Test Cases")
    st.write(response.choices[0].message.content)

# ------------------------------
# Generate Test Scenarios
# ------------------------------
if scenario_btn:
    prompt = f"""
You are a senior QA engineer.

Generate high-level test scenarios based on the following business requirement, feature, or issue.

Title / Requirement / Feature: {title}
Context: {context}

Return the output with these sections:
Functional Scenarios
Negative Scenarios
Edge / Boundary Scenarios
Regression Considerations

Keep the scenarios high-level, practical, and suitable for review by leadership, product owners, and business stakeholders.
Do not generate low-level step-by-step test cases unless absolutely necessary.
"""

    with st.spinner("Generating test scenarios..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

    st.subheader("Generated Test Scenarios")
    st.write(response.choices[0].message.content)
