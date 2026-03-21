import os
import json
import base64
from io import BytesIO

import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

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
# Session state init
# ------------------------------
if "generated_type" not in st.session_state:
    st.session_state.generated_type = None

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "generated_df" not in st.session_state:
    st.session_state.generated_df = None

if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------
# Helper functions
# ------------------------------
def encode_uploaded_image(uploaded_file):
    """Convert uploaded image file to base64 data URL."""
    image_bytes = uploaded_file.read()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{encoded}"

def safe_filename(text):
    """Convert title into safe filename."""
    cleaned = "".join(c if c.isalnum() or c in (" ", "_", "-") else "" for c in text)
    cleaned = cleaned.strip().replace(" ", "_").lower()
    return cleaned if cleaned else "ai_output"

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def convert_df_to_excel(df, sheet_name="AI_Output"):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Header formatting
        header_fill = PatternFill(fill_type="solid", start_color="D9EAF7", end_color="D9EAF7")
        header_font = Font(bold=True)
        wrap_alignment = Alignment(wrap_text=True, vertical="top")

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = wrap_alignment

        # Body formatting and auto column width
        for col_idx, column_cells in enumerate(worksheet.columns, start=1):
            max_length = 0
            col_letter = get_column_letter(col_idx)

            for cell in column_cells:
                cell.alignment = wrap_alignment
                try:
                    cell_value = str(cell.value) if cell.value is not None else ""
                    max_length = max(max_length, len(cell_value))
                except Exception:
                    pass

            adjusted_width = min(max(max_length + 2, 15), 50)
            worksheet.column_dimensions[col_letter].width = adjusted_width

        # Freeze header
        worksheet.freeze_panes = "A2"

    return output.getvalue()

def parse_json_response(content):
    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)

def add_to_history(output_type, title, pretty_text, df):
    st.session_state.history.insert(0, {
        "type": output_type,
        "title": title,
        "text": pretty_text,
        "df": df.copy() if df is not None else None
    })

    # Keep only latest 10 items
    st.session_state.history = st.session_state.history[:10]

# ------------------------------
# OpenAI generators
# ------------------------------
def generate_bug_report_with_optional_image(title, context, uploaded_file):
    text_prompt = f"""
You are a senior QA engineer.

Generate a professional bug report for the following issue.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "bug_report": {{
    "Title": "",
    "Description": "",
    "Steps to Reproduce": "",
    "Expected Result": "",
    "Actual Result": "",
    "Severity": "",
    "Priority": "",
    "Environment": "",
    "Observed UI / Screenshot Notes": "",
    "Assumptions": ""
  }}
}}

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
                            "image_url": {"url": image_data_url}
                        }
                    ]
                }
            ]
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text_prompt}]
        )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    bug_report = parsed["bug_report"]

    pretty_text = "\n".join([f"{k}: {v}" for k, v in bug_report.items()])
    df = pd.DataFrame([bug_report])

    return pretty_text, df

def generate_test_cases(title, context):
    prompt = f"""
You are a senior QA engineer.

Generate detailed QA test cases for the following issue, feature, or requirement.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "test_cases": [
    {{
      "Test Case ID": "TC_001",
      "Category": "Functional",
      "Scenario": "",
      "Preconditions": "",
      "Steps": "",
      "Expected Result": "",
      "Priority": "",
      "Type": "Positive"
    }}
  ]
}}

Rules:
- Include a mix of Functional, Negative, Edge, and Regression test cases.
- Keep test cases practical, concise, and useful for QA execution.
- Steps should be in a single text field with numbered steps.
- Return at least 8 test cases when possible.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    test_cases = parsed["test_cases"]

    pretty_lines = []
    for tc in test_cases:
        pretty_lines.append(
            f"""Test Case ID: {tc.get('Test Case ID', '')}
Category: {tc.get('Category', '')}
Scenario: {tc.get('Scenario', '')}
Preconditions: {tc.get('Preconditions', '')}
Steps: {tc.get('Steps', '')}
Expected Result: {tc.get('Expected Result', '')}
Priority: {tc.get('Priority', '')}
Type: {tc.get('Type', '')}
"""
        )

    pretty_text = "\n" + ("\n" + "-" * 80 + "\n").join(pretty_lines)
    df = pd.DataFrame(test_cases)

    return pretty_text, df

def generate_test_scenarios(title, context):
    prompt = f"""
You are a senior QA engineer.

Generate high-level test scenarios based on the following business requirement, feature, or issue.

Title / Requirement / Feature: {title}
Context: {context}

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{{
  "test_scenarios": [
    {{
      "Scenario ID": "TS_001",
      "Category": "Functional",
      "Scenario": "",
      "Description": "",
      "Priority": "",
      "Notes": ""
    }}
  ]
}}

Rules:
- Include Functional, Negative, Edge / Boundary, and Regression scenarios.
- Keep scenarios high-level, practical, and suitable for leadership, product owners, and business stakeholders.
- Do not generate low-level step-by-step test cases.
- Return at least 8 scenarios when possible.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    parsed = parse_json_response(content)
    scenarios = parsed["test_scenarios"]

    pretty_lines = []
    for sc in scenarios:
        pretty_lines.append(
            f"""Scenario ID: {sc.get('Scenario ID', '')}
Category: {sc.get('Category', '')}
Scenario: {sc.get('Scenario', '')}
Description: {sc.get('Description', '')}
Priority: {sc.get('Priority', '')}
Notes: {sc.get('Notes', '')}
"""
        )

    pretty_text = "\n" + ("\n" + "-" * 80 + "\n").join(pretty_lines)
    df = pd.DataFrame(scenarios)

    return pretty_text, df

# ------------------------------
# Display helpers
# ------------------------------
def show_download_buttons(df, pretty_text, base_name, sheet_name):
    csv_data = convert_df_to_csv(df)
    excel_data = convert_df_to_excel(df, sheet_name=sheet_name)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download TXT",
            data=pretty_text,
            file_name=f"{base_name}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{base_name}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"{base_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

def render_current_output():
    if st.session_state.generated_type and st.session_state.generated_df is not None:
        output_type = st.session_state.generated_type
        result_text = st.session_state.generated_text
        df = st.session_state.generated_df
        base_name = st.session_state.generated_base_name
        sheet_name = st.session_state.generated_sheet_name

        st.subheader(f"Generated {output_type}")
        st.dataframe(df, use_container_width=True)

        st.text_area(
            "Copy Output",
            value=result_text,
            height=280
        )

        show_download_buttons(df, result_text, base_name, sheet_name)

def render_history():
    if not st.session_state.history:
        return

    with st.expander("View Recent History"):
        for idx, item in enumerate(st.session_state.history, start=1):
            st.markdown(f"**{idx}. {item['type']} — {item['title']}**")
            if item["df"] is not None:
                st.dataframe(item["df"], use_container_width=True)
            st.text_area(
                f"History Output {idx}",
                value=item["text"],
                height=180,
                key=f"history_text_{idx}"
            )
            st.markdown("---")

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
    st.info("Enter Title and Context to enable Bug Report, Test Cases, and Test Scenarios.")

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
# Actions
# ------------------------------
if bug_btn:
    try:
        with st.spinner("Generating bug report..."):
            result_text, df_bug = generate_bug_report_with_optional_image(title, context, uploaded_file)

        base_name = f"{safe_filename(title)}_bug_report"

        st.session_state.generated_type = "Bug Report"
        st.session_state.generated_text = result_text
        st.session_state.generated_df = df_bug
        st.session_state.generated_base_name = base_name
        st.session_state.generated_sheet_name = "Bug_Report"

        add_to_history("Bug Report", title, result_text, df_bug)

    except Exception as e:
        st.error(f"Failed to generate bug report: {e}")

if case_btn:
    try:
        with st.spinner("Generating test cases..."):
            result_text, df_cases = generate_test_cases(title, context)

        base_name = f"{safe_filename(title)}_test_cases"

        st.session_state.generated_type = "Test Cases"
        st.session_state.generated_text = result_text
        st.session_state.generated_df = df_cases
        st.session_state.generated_base_name = base_name
        st.session_state.generated_sheet_name = "Test_Cases"

        add_to_history("Test Cases", title, result_text, df_cases)

    except Exception as e:
        st.error(f"Failed to generate test cases: {e}")

if scenario_btn:
    try:
        with st.spinner("Generating test scenarios..."):
            result_text, df_scenarios = generate_test_scenarios(title, context)

        base_name = f"{safe_filename(title)}_test_scenarios"

        st.session_state.generated_type = "Test Scenarios"
        st.session_state.generated_text = result_text
        st.session_state.generated_df = df_scenarios
        st.session_state.generated_base_name = base_name
        st.session_state.generated_sheet_name = "Test_Scenarios"

        add_to_history("Test Scenarios", title, result_text, df_scenarios)

    except Exception as e:
        st.error(f"Failed to generate test scenarios: {e}")

# ------------------------------
# Render output + history
# ------------------------------
render_current_output()
render_history()

# ------------------------------
# Optional clear button
# ------------------------------
if st.session_state.generated_type:
    if st.button("Clear Current Output", use_container_width=True):
        st.session_state.generated_type = None
        st.session_state.generated_text = ""
        st.session_state.generated_df = None
        st.session_state.generated_base_name = ""
        st.session_state.generated_sheet_name = ""
        st.rerun()
