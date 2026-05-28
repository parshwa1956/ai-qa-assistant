"""Prompt templates ported from Streamlit Kaldi One."""

OUTPUT_TYPES = {
    "qa": ["Bug Report", "Test Cases", "Test Scenarios"],
    "ba": [
        "Requirement to User Story",
        "Acceptance Criteria Generator",
        "Business Requirement Breakdown",
        "User Story + Acceptance Criteria + Traceability",
        "Business Process Flow",
        "Data Flow Diagram",
    ],
    "dev": [
        "Technical Task Breakdown",
        "API / Backend Tasks",
        "Developer Checklist",
        "Smart Code Review",
        "Technical Flow Diagram",
    ],
    "flow": ["Flow to Requirement"],
}


def bug_report_prompt(title: str, context: str) -> str:
    return f"""
You are a senior QA engineer.
Generate a professional bug report for the following issue.
Title / Requirement / Feature: {title}
Context: {context}
Return ONLY valid JSON. Do not add markdown.
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
"""


def test_cases_prompt(title: str, context: str) -> str:
    return f"""
You are a senior QA engineer.
Generate detailed QA test cases for the following issue, feature, or requirement.
Title / Requirement / Feature: {title}
Context: {context}
Return ONLY valid JSON.
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
"""


def test_scenarios_prompt(title: str, context: str) -> str:
    return f"""
You are a senior QA engineer.
Generate high-level test scenarios based on the following business requirement, feature, or issue.
Title / Requirement / Feature: {title}
Context: {context}
Return ONLY valid JSON.
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
"""


def ba_prompt(title: str, context: str, output_type: str) -> str:
    templates = {
        "Requirement to User Story": f"""
You are a senior business analyst.
Convert the following requirement into structured user stories.
Title: {title}
Requirement Details: {context}
Return ONLY valid JSON.
Use: {{"user_stories": [{{"User Story ID": "US_001", "As a": "", "I want": "", "So that": "", "Priority": "", "Notes": ""}}]}}
""",
        "Acceptance Criteria Generator": f"""
You are a senior business analyst.
Generate clear acceptance criteria for the following requirement.
Title: {title}
Requirement Details: {context}
Return ONLY valid JSON.
Use: {{"acceptance_criteria": [{{"AC ID": "AC_001", "Criteria": "", "Type": "", "Priority": ""}}]}}
""",
        "Business Requirement Breakdown": f"""
You are a senior business analyst.
Break down the following requirement into structured business requirement points.
Title: {title}
Requirement Details: {context}
Return ONLY valid JSON.
Use: {{"requirement_breakdown": [{{"Section": "", "Details": "", "Priority": "", "Notes": ""}}]}}
""",
    }
    return templates[output_type]


def traceability_prompt(title: str, context: str, source_filename: str = "") -> str:
    return f"""
You are a senior business analyst.
Convert the requirement into structured user stories with detailed acceptance criteria and rich traceability.
Title: {title}
Requirement Details: {context}
Source File Name: {source_filename}
Return ONLY valid JSON.
Use structure with "stories" array including Traceability list per story.
"""


def dev_prompt(title: str, context: str, output_type: str) -> str:
    templates = {
        "Technical Task Breakdown": f"""
You are a senior software engineer.
Break down the following requirement into technical development tasks.
Title: {title}
Technical Context: {context}
Return ONLY valid JSON.
Use: {{"technical_tasks": [{{"Task ID": "DEV_001", "Task": "", "Component": "", "Priority": "", "Notes": ""}}]}}
""",
        "API / Backend Tasks": f"""
You are a senior backend engineer.
Generate backend and API development tasks.
Title: {title}
Technical Context: {context}
Return ONLY valid JSON.
Use: {{"api_tasks": [{{"Task ID": "API_001", "Task": "", "Endpoint / Service": "", "Priority": "", "Notes": ""}}]}}
""",
        "Developer Checklist": f"""
You are a senior software engineer.
Generate a developer checklist.
Title: {title}
Technical Context: {context}
Return ONLY valid JSON.
Use: {{"developer_checklist": [{{"Checklist Item": "", "Category": "", "Priority": "", "Notes": ""}}]}}
""",
    }
    return templates[output_type]


def flow_diagram_prompt(title: str, context: str, diagram_type: str) -> str:
    return f"""
You are a senior business systems analyst and solution architect.
Based on the requirement below, generate a {diagram_type}.
Title: {title}
Requirement Details: {context}
Return ONLY valid JSON.
Use: {{"diagram_output": {{"diagram_type": "{diagram_type}", "mermaid_code": "flowchart TD\\n    A[Start] --> B[Process]", "steps": [{{"Step ID": "STEP_001", "From": "", "To": "", "Action": "", "Decision": "", "Notes": ""}}]}}}}
"""


def flow_requirements_prompt() -> str:
    return """
Analyze this flow diagram or process file and generate concise business requirements.
Return ONLY valid JSON.
Use: {"requirements": {"Process Summary": "", "What Happens from Start to Finish": [], "Important Decisions": [], "Test Data Needed": []}}
"""


def code_review_prompt(code_input: str) -> str:
    return f"""
You are a senior software engineer performing a smart code review.
Review the code below and return ONLY valid JSON with success, summary, issues, recommendations.
Code to review:
{code_input}
"""
