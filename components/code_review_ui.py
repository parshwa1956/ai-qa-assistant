import json
import streamlit as st


def get_severity_color(severity):
    severity = str(severity or "").strip().lower()
    if severity == "high":
        return "#ff4b4b"
    if severity == "medium":
        return "#f39c12"
    if severity == "low":
        return "#2ecc71"
    return "#6c757d"


def detect_code_language(issue):
    raw = str(issue.get("language") or "").strip().lower()
    if raw:
        return raw

    file_name = str(issue.get("file") or "").strip().lower()

    if file_name.endswith(".py"):
        return "python"
    if file_name.endswith(".js"):
        return "javascript"
    if file_name.endswith(".ts"):
        return "typescript"
    if file_name.endswith(".java"):
        return "java"
    if file_name.endswith(".cs"):
        return "csharp"
    if file_name.endswith(".sql"):
        return "sql"
    if file_name.endswith(".json"):
        return "json"

    return "python"


def normalize_summary(review_result, issues):
    summary = review_result.get("summary", {})

    if isinstance(summary, dict):
        total_issues = int(summary.get("total_issues", len(issues) if issues else 0))
        high = int(summary.get("high", 0))
        medium = int(summary.get("medium", 0))
        low = int(summary.get("low", 0))
        overall_health = summary.get("overall_health", "Unknown")
        summary_text = summary.get("text", "")
    else:
        total_issues = len(issues) if issues else 0
        high = sum(1 for i in issues if str(i.get("severity", "")).lower() == "high")
        medium = sum(1 for i in issues if str(i.get("severity", "")).lower() == "medium")
        low = sum(1 for i in issues if str(i.get("severity", "")).lower() == "low")
        overall_health = review_result.get("overall_health", "Unknown")
        summary_text = str(summary or "")

    return {
        "total_issues": total_issues,
        "high": high,
        "medium": medium,
        "low": low,
        "overall_health": overall_health,
        "summary_text": summary_text,
    }


def build_issue_download_text(idx, issue):
    title = issue.get("title", "Untitled Issue")
    file_name = issue.get("file", "Unknown file")
    function_name = issue.get("function", "Unknown function")
    line_no = issue.get("line", "N/A")
    severity = issue.get("severity", "Unknown")
    category = issue.get("category", "General")
    current_code = issue.get("current_code", "")
    explanation = issue.get("explanation", "No explanation provided.")
    future_risk = issue.get("future_risk", "No future risk provided.")
    recommendation = issue.get("recommendation", "No recommendation provided.")
    suggested_code = issue.get("suggested_code", "")
    impact = issue.get("impact", "No impact provided.")

    return f"""Issue {idx}: {title}

File: {file_name}
Function: {function_name}
Line: {line_no}
Severity: {severity}
Category: {category}

Why it matters:
{explanation}

Future risk:
{future_risk}

Recommendation:
{recommendation}

Impact if not fixed:
{impact}

Current Code:
{current_code}

Suggested Code:
{suggested_code}
"""


def render_fallback_json(review_result):
    st.markdown("### Raw Review Result")
    try:
        st.json(review_result)
    except Exception:
        st.code(json.dumps(review_result, indent=2), language="json")


def render_code_review_results(review_result):
    if not review_result:
        st.warning("No review results available.")
        return

    if not isinstance(review_result, dict):
        st.error("Invalid code review result format.")
        st.write(review_result)
        return

    success = review_result.get("success", True)
    error = review_result.get("error", "")
    issues = review_result.get("issues", [])

    if not isinstance(issues, list):
        issues = []

    summary_data = normalize_summary(review_result, issues)

    st.markdown("## Smart Code Review Results")

    if not success:
        st.error("Smart code review service returned an error.")
        if error:
            st.code(str(error))
        render_fallback_json(review_result)
        return

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Issues", summary_data["total_issues"])
    col2.metric("High", summary_data["high"])
    col3.metric("Medium", summary_data["medium"])
    col4.metric("Low", summary_data["low"])
    col5.metric("Code Health", summary_data["overall_health"])

    if summary_data["summary_text"]:
        st.info(summary_data["summary_text"])

    st.markdown("---")

    if not issues:
        st.success("No issues found. Code looks clean.")
        recommendations = review_result.get("recommendations", [])
        if isinstance(recommendations, list) and recommendations:
            st.markdown("### Recommendations")
            for rec in recommendations:
                st.write(f"- {rec}")
        return

    severity_filter = st.selectbox(
        "Filter issues by severity",
        ["All", "High", "Medium", "Low"],
        index=0,
        key="code_review_severity_filter",
    )

    filtered_issues = issues
    if severity_filter != "All":
        filtered_issues = [
            item
            for item in issues
            if str(item.get("severity", "")).strip().lower() == severity_filter.lower()
        ]

    if not filtered_issues:
        st.info("No issues match the selected severity filter.")
        return

    for idx, issue in enumerate(filtered_issues, start=1):
        if not isinstance(issue, dict):
            st.warning(f"Issue {idx} has an invalid format.")
            st.write(issue)
            continue

        title = issue.get("title", "Untitled Issue")
        file_name = issue.get("file", "Unknown file")
        function_name = issue.get("function", "Unknown function")
        line_no = issue.get("line", "N/A")
        severity = issue.get("severity", "Unknown")
        category = issue.get("category", "General")
        current_code = issue.get("current_code", "")
        explanation = issue.get("explanation", "No explanation provided.")
        future_risk = issue.get("future_risk", "No future risk provided.")
        recommendation = issue.get("recommendation", "No recommendation provided.")
        suggested_code = issue.get("suggested_code", "")
        impact = issue.get("impact", "No impact provided.")
        language = detect_code_language(issue)

        severity_color = get_severity_color(severity)

        st.markdown(
            f"""
            <div style="
                border: 1px solid #e6e6e6;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
                background-color: #ffffff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <h4 style="margin:0;">Issue {idx}: {title}</h4>
                        <p style="margin:6px 0 0 0; color:#555;">
                            <strong>File:</strong> {file_name} &nbsp;&nbsp;
                            <strong>Function:</strong> {function_name} &nbsp;&nbsp;
                            <strong>Line:</strong> {line_no}
                        </p>
                    </div>
                    <div style="
                        background-color:{severity_color};
                        color:white;
                        padding:6px 12px;
                        border-radius:20px;
                        font-size:13px;
                        font-weight:bold;
                    ">
                        {severity}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"View details for Issue {idx}", expanded=False):
            left_col, right_col = st.columns(2)

            with left_col:
                st.markdown(f"**Category:** {category}")
                st.markdown(f"**Why it matters:** {explanation}")
                st.markdown(f"**Future risk:** {future_risk}")

            with right_col:
                st.markdown(f"**Recommendation:** {recommendation}")
                st.markdown(f"**Impact if not fixed:** {impact}")

            if current_code:
                st.markdown("**Current Code**")
                st.code(current_code, language=language)

            if suggested_code:
                st.markdown("**Suggested Improved Code**")
                st.code(suggested_code, language=language)

            quick_fix_summary = f"""Issue: {title}
File: {file_name}
Function: {function_name}
Line: {line_no}
Severity: {severity}

Why:
{explanation}

Fix:
{recommendation}"""

            st.text_area(
                "Quick Fix Summary",
                value=quick_fix_summary,
                height=180,
                key=f"summary_{idx}",
            )

            st.download_button(
                label=f"Download Issue {idx} Details",
                data=build_issue_download_text(idx, issue),
                file_name=f"issue_{idx}_review.txt",
                mime="text/plain",
                key=f"download_issue_{idx}",
            )

    recommendations = review_result.get("recommendations", [])
    if isinstance(recommendations, list) and recommendations:
        st.markdown("### Overall Recommendations")
        for rec in recommendations:
            st.write(f"- {rec}")
