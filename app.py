import os
import base64
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
# Helper functions
# ------------------------------
def encode_uploaded_image(uploaded_file):
    """Convert uploaded image file to base64 data URL."""
    image_bytes = uploaded_file.read()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{encoded}"

def generate_bug_report_with_optional_image(title, context, uploaded_file):
    """Generate bug report using text only or text + screenshot."""
    text_prompt = f"""
You are a senior QA engineer.

Generate a professional bug report for the following issue.

Title / Requirement / Feature: {title}
Context: {context}

Return the output with these sections:
Title
Description
Steps to Reproduce
Expected Result
Actual Result
Severity
Environment
Observed UI / Screenshot Notes
Assumptions

Rules:
- Be practical, realistic, and ready to copy into Jira or Azure DevOps.
- If a screenshot is provided, analyze the visible UI issue and use it to improve the bug report.
- Do not invent certainty where the screenshot alone cannot prove something.
- Clearly mark assumptions.
"""

    if uploaded_file is not None:
        image_data_url = encode_uploaded_image(uploaded_file)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        }
                    ]
                }
            ]
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": text_prompt}
            ]
        )

    return response.choices[0].message.content

def generate_test_cases(title, context):
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_test_scenarios(title, context):
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

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
    placeholder="Example: Login button not working on Safari mobile"
)

context = st.text_area(
    "Context / Business Requirement Details *",
    height=150,
    placeholder="Paste bug details, requirement details, acceptance criteria, or observations here..."
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
# Bug Report
# ------------------------------
if bug_btn:
    with st.spinner("Generating bug report..."):
        result = generate_bug_report_with_optional_image(title, context, uploaded_file)

    st.subheader("Generated Bug Report")
    st.code(result, language=None)

    st.download_button(
        label="Download Bug Report",
        data=result,
        file_name="bug_report.txt",
        mime="text/plain"
    )

# ------------------------------
# Test Cases
# ------------------------------
if case_btn:
    with st.spinner("Generating test cases..."):
        result = generate_test_cases(title, context)

    st.subheader("Generated Test Cases")
    st.code(result, language=None)

    st.download_button(
        label="Download Test Cases",
        data=result,
        file_name="test_cases.txt",
        mime="text/plain"
    )

# ------------------------------
# Test Scenarios
# ------------------------------
if scenario_btn:
    with st.spinner("Generating test scenarios..."):
        result = generate_test_scenarios(title, context)

    st.subheader("Generated Test Scenarios")
    st.code(result, language=None)

    st.download_button(
        label="Download Test Scenarios",
        data=result,
        file_name="test_scenarios.txt",
        mime="text/plain"
    )
