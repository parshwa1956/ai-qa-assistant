import os
import json
import base64
from io import BytesIO
from datetime import datetime

import pandas as pd
import requests
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
    st.error("OpenAI API key not found. Add it in Streamlit secrets or local .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# Load Jira settings
# ------------------------------
jira_base_url = None
jira_email = None
jira_api_token = None
jira_project_key = None

try:
    jira_base_url = st.secrets["JIRA_BASE_URL"]
    jira_email = st.secrets["JIRA_EMAIL"]
    jira_api_token = st.secrets["JIRA_API_TOKEN"]
    jira_project_key = st.secrets["JIRA_PROJECT_KEY"]
except Exception:
    jira_base_url = os.getenv("JIRA_BASE_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_project_key = os.getenv("JIRA_PROJECT_KEY")

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="AI QA Assistant",
    page_icon="🧪",
    layout="wide",
)

# ------------------------------
# Light layout tweak
# ------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1600px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.small-muted {
    color: #6b7280;
    font-size: 0.85rem;
}

.sidebar-project-title {
    font-weight: 600;
    font-size: 0.96rem;
    margin-top: 0.25rem;
    margin-bottom: 0.15rem;
}

.sidebar-section-label {
    color: #6b7280;
    font-size: 0.82rem;
    margin-top: 0.5rem;
    margin-bottom: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.sidebar-item-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 8px 10px;
    background: #ffffff;
    margin-bottom: 8px;
}

.sidebar-project-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 10px 12px;
    background: #fafafa;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Session state init
# ------------------------------
def init_session_state():
    defaults = {
        "generated_type": None,
        "generated_text": "",
        "generated_df": None,
        "generated_title": "",
        "generated_base_name": "",
        "generated_sheet_name": "",
        "history": [],
        "flow_generated_text": "",
        "flow_generated_title": "",
        "flow_generated_df": None,
        "flow_generated_base_name": "",
        "flow_uploaded_name": "",
        "projects": {"General": []},
        "selected_project": "General",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ------------------------------
# Helper functions
# ------------------------------
def encode_uploaded_image(uploaded_file):
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = uploaded_file.type
    return f"data:{mime_type};base64,{encoded}"

def safe_filename(text):
    cleaned = "".join(c if c.isalnum() or c in (" ", "_", "-") else "" for c in text)
    cleaned = cleaned.strip().replace(" ", "_").lower()
    return cleaned if cleaned else "ai_output"

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def convert_df_to_excel(df, sheet_name="AI_Output"):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        header_fill = PatternFill(fill_type="solid", start_color="D9EAF7", end_color="D9EAF7")
        header_font = Font(bold=True)
        wrap_alignment = Alignment(wrap_text=True, vertical="top")

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = wrap_alignment

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

        worksheet.freeze_panes = "A2"

    return output.getvalue()

def parse_json_response(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)

def add_to_history(output_type, title, pretty_text, df):
    record = {
        "type": output_type,
        "title": title,
        "text": pretty_text,
        "df": df.copy() if df is not None else None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:10]
    save_to_project(record)

def save_to_project(record):
    selected_project = st.session_state.selected_project
    if selected_project not in st.session_state.projects:
        st.session_state.projects[selected_project] = []

    project_record = {
        "type": record["type"],
        "title": record["title"],
        "text": record["text"],
        "df": record["df"].copy() if record["df"] is not None else None,
        "created_at": record["created_at"]
    }

    st.session_state.projects[selected_project].insert(0, project_record)

def load_project_item_into_current_output(item):
    st.session_state.generated_type = item["type"]
    st.session_state.generated_title = item["title"]
    st.session_state.generated_text = item["text"]
    st.session_state.generated_df = item["df"].copy() if item["df"] is not None else None
    st.session_state.generated_base_name = safe_filename(item["title"])

    if item["type"] == "Bug Report":
        st.session_state.generated_sheet_name = "Bug_Report"
    elif item["type"] == "Test Cases":
        st.session_state.generated_sheet_name = "Test_Cases"
    elif item["type"] == "Test Scenarios":
        st.session_state.generated_sheet_name = "Test_Scenarios"
    else:
        st.session_state.generated_sheet_name = "AI_Output"

def delete_project(project_name):
    if project_name == "General":
        return False, "You cannot delete the default General project."

    if project_name in st.session_state.projects:
        del st.session_state.projects[project_name]
        st.session_state.selected_project = "General"
        return True, f"Project '{project_name}' deleted."

    return False, "Project not found."

def get_default_jira_issue_type(output_type):
    mapping = {
        "Bug Report": "Bug",
        "Test Cases": "Task",
        "Test Scenarios": "Story"
    }
    return mapping.get(output_type, "Task")

def get_default_jira_labels(output_type):
    mapping = {
        "Bug Report": ["bug"],
        "Test Cases": ["task"],
        "Test Scenarios": ["story"]
    }
    return mapping.get(output_type, ["task"])

def build_jira_description_doc(description_text):
    lines = [line.strip() for line in description_text.splitlines() if line.strip()]

    content_blocks = []
    for line in lines:
        content_blocks.append({
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": line[:3000]
                }
            ]
        })

    if not content_blocks:
        content_blocks = [{
            "type": "paragraph",
            "content": [{"type": "text", "text": "No description provided."}]
        }]

    return {
        "type": "doc",
        "version": 1,
        "content": content_blocks
    }

def create_jira_issue(summary, description, issue_type="Task", labels=None):
    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        return False, "Jira settings are missing in Streamlit secrets or .env."

    url = f"{jira_base_url}/rest/api/3/issue"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    auth = (jira_email, jira_api_token)

    payload = {
        "fields": {
            "project": {"key": jira_project_key},
            "summary": summary,
            "description": build_jira_description_doc(description),
            "issuetype": {"name": issue_type},
            "labels": labels or []
        }
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code in [200, 201]:
        data = response.json()
        return True, data.get("key", "Created")

    return False, response.text

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
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }]
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

def reset_flow_output_if_new_file(uploaded_flow):
    if uploaded_flow is None:
        return

    if st.session_state.flow_uploaded_name != uploaded_flow.name:
        st.session_state.flow_generated_text = ""
        st.session_state.flow_generated_title = ""
        st.session_state.flow_generated_df = None
        st.session_state.flow_generated_base_name = ""
        st.session_state.flow_uploaded_name = uploaded_flow.name

def generate_requirements_from_flow(uploaded_flow):
    prompt = """
Analyze this flow diagram and generate concise business requirements.

Return ONLY valid JSON.
Do not add markdown.
Do not add explanation text.

Use this exact JSON structure:
{
  "requirements": {
    "Process Summary": "",
    "What Happens from Start to Finish": [
      "Step 1",
      "Step 2",
      "Step 3"
    ],
    "Important Decisions": [
      "Decision 1",
      "Decision 2"
    ],
    "Test Data Needed": [
      "Data Point 1",
      "Data Point 2"
    ]
  }
}

Rules:
- Explain the diagram in simple language for a general audience.
- Clearly describe what happens from the beginning to the end of the process.
- Keep the output short, clear, and business-friendly.
- Focus only on the main flow.
- Do not add too much technical detail.
- If any part is unclear, say "Needs review" instead of guessing.
"""

    if uploaded_flow.type in ["image/png", "image/jpg", "image/jpeg"]:
        image_data_url = encode_uploaded_image(uploaded_flow)
        uploaded_flow.seek(0)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }]
        )
        content = response.choices[0].message.content

    elif uploaded_flow.type == "application/pdf":
        file_bytes = uploaded_flow.read()
        uploaded_flow.seek(0)

        uploaded_pdf = client.files.create(
            file=(uploaded_flow.name, file_bytes, "application/pdf"),
            purpose="user_data"
        )

        response = client.responses.create(
            model="gpt-4.1",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_file", "file_id": uploaded_pdf.id}
                ]
            }]
        )

        content = response.output_text
    else:
        raise ValueError("Unsupported file type. Please upload PNG, JPG, JPEG, or PDF.")

    parsed = parse_json_response(content)
    req = parsed["requirements"]

    steps_text = "\n".join([f"{idx + 1}. {step}" for idx, step in enumerate(req.get("What Happens from Start to Finish", []))])
    decisions_text = "\n".join([f"- {item}" for item in req.get("Important Decisions", [])])
    test_data_text = "\n".join([f"- {item}" for item in req.get("Test Data Needed", [])])

    pretty_text = f"""Process Summary:
{req.get('Process Summary', '')}

What Happens from Start to Finish:
{steps_text}

Important Decisions:
{decisions_text}

Test Data Needed:
{test_data_text}
"""

    df = pd.DataFrame([{
        "Process Summary": req.get("Process Summary", ""),
        "What Happens from Start to Finish": steps_text,
        "Important Decisions": decisions_text,
        "Test Data Needed": test_data_text
    }])

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
        generated_title = st.session_state.generated_title

        st.subheader(f"Generated {output_type}")
        st.dataframe(df, use_container_width=True)

        st.text_area(
            "Copy Output",
            value=result_text,
            height=280,
            key=f"copy_output_{output_type}"
        )

        show_download_buttons(df, result_text, base_name, sheet_name)

        st.markdown("### Jira")

        default_issue_type = get_default_jira_issue_type(output_type)
        default_labels = get_default_jira_labels(output_type)

        issue_type_options = ["Bug", "Task", "Story"]
        default_index = issue_type_options.index(default_issue_type) if default_issue_type in issue_type_options else 0

        jira_issue_type = st.selectbox(
            "Issue Type",
            issue_type_options,
            index=default_index,
            key=f"jira_issue_type_{output_type}"
        )

        if st.button("Create in Jira", use_container_width=True, key=f"create_jira_{output_type}"):
            with st.spinner("Creating Jira issue..."):
                success, message = create_jira_issue(
                    summary=generated_title,
                    description=result_text,
                    issue_type=jira_issue_type,
                    labels=default_labels
                )

            if success:
                issue_url = f"{jira_base_url}/browse/{message}" if jira_base_url else ""
                st.success(f"Jira issue created successfully: {message}")
                if issue_url:
                    st.markdown(f"[Open Jira Issue]({issue_url})")
            else:
                st.error(f"Failed to create Jira issue: {message}")

def render_flow_output():
    if st.session_state.flow_generated_df is not None:
        st.subheader("Generated Requirements")
        st.dataframe(st.session_state.flow_generated_df, use_container_width=True)

        st.text_area(
            "Copy Output",
            value=st.session_state.flow_generated_text,
            height=320,
            key="copy_output_flow_requirements"
        )

        show_download_buttons(
            st.session_state.flow_generated_df,
            st.session_state.flow_generated_text,
            st.session_state.flow_generated_base_name,
            "Flow_Requirements"
        )

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

def render_sidebar_projects():
    st.sidebar.markdown("### Projects")

    new_project = st.sidebar.text_input(
        "New project",
        placeholder="Example: Salesforce Regression",
        key="sidebar_new_project_name"
    )

    if st.sidebar.button("Add Project", use_container_width=True, key="sidebar_add_project_btn"):
        project_name = new_project.strip()
        if not project_name:
            st.sidebar.warning("Enter a project name.")
        elif project_name in st.session_state.projects:
            st.sidebar.warning("Project already exists.")
        else:
            st.session_state.projects[project_name] = []
            st.session_state.selected_project = project_name
            st.rerun()

    project_names = list(st.session_state.projects.keys())

    selected_project = st.sidebar.selectbox(
        "Select Project",
        project_names,
        index=project_names.index(st.session_state.selected_project) if st.session_state.selected_project in project_names else 0,
        key="sidebar_selected_project_box"
    )
    st.session_state.selected_project = selected_project

    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        if st.button("Open", use_container_width=True, key="sidebar_open_project_btn"):
            st.session_state.selected_project = selected_project
    with col_b:
        if st.button("Delete", use_container_width=True, key="sidebar_delete_project_btn"):
            success, msg = delete_project(selected_project)
            if success:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.warning(msg)

    project_items = st.session_state.projects.get(selected_project, [])

    st.sidebar.markdown(
        f"""
        <div class="sidebar-project-card">
            <div class="sidebar-project-title">{selected_project}</div>
            <div class="small-muted">{len(project_items)} saved item(s)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown('<div class="sidebar-section-label">Recent</div>', unsafe_allow_html=True)

    if not project_items:
        st.sidebar.caption("No saved items yet.")
        return

    for idx, item in enumerate(project_items[:20]):
        st.sidebar.markdown(
            f"""
            <div class="sidebar-item-card">
                <strong>{item['title']}</strong><br>
                <span class="small-muted">{item['type']} • {item['created_at']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        open_col, delete_col = st.sidebar.columns(2)
        with open_col:
            if st.button("Open", key=f"sidebar_open_item_{selected_project}_{idx}", use_container_width=True):
                load_project_item_into_current_output(item)
                st.rerun()
        with delete_col:
            if st.button("Delete", key=f"sidebar_delete_item_{selected_project}_{idx}", use_container_width=True):
                del st.session_state.projects[selected_project][idx]
                st.rerun()

# ------------------------------
# Sidebar
# ------------------------------
render_sidebar_projects()

# ------------------------------
# Header
# ------------------------------
st.title("AI QA Assistant")
st.write("Generate bug reports, test cases, high-level test scenarios, and flow-based requirements using AI.")

tab1, tab2 = st.tabs(["QA Generator", "Flow to Requirements"])

# ------------------------------
# Tab 1: QA Generator
# ------------------------------
with tab1:
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
        type=["png", "jpg", "jpeg"],
        key="qa_screenshot_upload"
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)

    is_form_valid = bool(title.strip()) and bool(context.strip())

    if is_form_valid:
        st.success("Looks good. You can now generate outputs.")
    else:
        st.info("Enter Title and Context to enable Bug Report, Test Cases, and Test Scenarios.")

    col1, col2, col3 = st.columns(3)

    with col1:
        bug_btn = st.button("Generate Bug Report", disabled=not is_form_valid, use_container_width=True)

    with col2:
        case_btn = st.button("Generate Test Cases", disabled=not is_form_valid, use_container_width=True)

    with col3:
        scenario_btn = st.button("Generate Test Scenarios", disabled=not is_form_valid, use_container_width=True)

    if bug_btn:
        try:
            with st.spinner("Generating bug report..."):
                result_text, df_bug = generate_bug_report_with_optional_image(title, context, uploaded_file)

            base_name = f"{safe_filename(title)}_bug_report"

            st.session_state.generated_type = "Bug Report"
            st.session_state.generated_title = title
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
            st.session_state.generated_title = title
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
            st.session_state.generated_title = title
            st.session_state.generated_text = result_text
            st.session_state.generated_df = df_scenarios
            st.session_state.generated_base_name = base_name
            st.session_state.generated_sheet_name = "Test_Scenarios"

            add_to_history("Test Scenarios", title, result_text, df_scenarios)

        except Exception as e:
            st.error(f"Failed to generate test scenarios: {e}")

    render_current_output()
    render_history()

    if st.session_state.generated_type:
        if st.button("Clear Current Output", use_container_width=True, key="clear_qa_output"):
            st.session_state.generated_type = None
            st.session_state.generated_title = ""
            st.session_state.generated_text = ""
            st.session_state.generated_df = None
            st.session_state.generated_base_name = ""
            st.session_state.generated_sheet_name = ""
            st.rerun()

# ------------------------------
# Tab 2: Flow to Requirements
# ------------------------------
with tab2:
    st.subheader("Flow Diagram to Requirements")
    st.caption("Upload a flow diagram and generate a simple explanation for general audience.")

    uploaded_flow = st.file_uploader(
        "Upload Flow Diagram",
        type=["png", "jpg", "jpeg", "pdf"],
        key="flow_diagram_upload"
    )

    if uploaded_flow is not None:
        reset_flow_output_if_new_file(uploaded_flow)

        if uploaded_flow.type in ["image/png", "image/jpg", "image/jpeg"]:
            st.image(uploaded_flow, caption="Uploaded Flow Diagram", use_container_width=True)
        elif uploaded_flow.type == "application/pdf":
            st.info(f"PDF uploaded: {uploaded_flow.name}")

    flow_btn = st.button(
        "Generate Requirements",
        disabled=uploaded_flow is None,
        use_container_width=True,
        key="generate_flow_requirements"
    )

    if uploaded_flow is None:
        st.info("Upload a flow diagram to enable Generate Requirements.")

    if flow_btn and uploaded_flow is not None:
        try:
            flow_title = uploaded_flow.name.rsplit(".", 1)[0]

            with st.spinner("Generating requirements from flow..."):
                result_text, df_flow = generate_requirements_from_flow(uploaded_flow)

            st.session_state.flow_generated_title = flow_title
            st.session_state.flow_generated_text = result_text
            st.session_state.flow_generated_df = df_flow
            st.session_state.flow_generated_base_name = f"{safe_filename(flow_title)}_requirements"

        except Exception as e:
            st.error(f"Failed to generate requirements: {e}")

    render_flow_output()

    if st.session_state.flow_generated_df is not None:
        if st.button("Clear Flow Output", use_container_width=True, key="clear_flow_output"):
            st.session_state.flow_generated_text = ""
            st.session_state.flow_generated_title = ""
            st.session_state.flow_generated_df = None
            st.session_state.flow_generated_base_name = ""
            st.rerun()
