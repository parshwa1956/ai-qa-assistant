import streamlit as st


def get_severity_color(severity):
    severity = str(severity).strip().lower()
    if severity == "high":
        return "#ff4b4b"
    elif severity == "medium":
        return "#f39c12"
    elif severity == "low":
        return "#2ecc71"
    return "#6c757d"


def render_code_review_results(review_result):
    if not review_result:
        st.warning("No review results available.")
        return

    summary = review_result.get("summary", {})
    issues = review_result.get("issues", [])

    st.markdown("## Smart Code Review Results")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Issues", summary.get("total_issues", 0))
    col2.metric("High", summary.get("high", 0))
    col3.metric("Medium", summary.get("medium", 0))
    col4.metric("Low", summary.get("low", 0))
    col5.metric("Code Health", summary.get("overall_health", "Unknown"))

    st.markdown("---")

    if not issues:
        st.success("No issues found. Code looks clean.")
        return

    severity_filter = st.selectbox(
        "Filter issues by severity",
        ["All", "High", "Medium", "Low"],
        index=0,
        key="code_review_severity_filter"
    )

    if severity_filter != "All":
        issues = [
            i for i in issues
            if str(i.get("severity", "")).lower() == severity_filter.lower()
        ]

    if not issues:
        st.info("No issues match the selected severity filter.")
        return

    for idx, issue in enumerate(issues, start=1):
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
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
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
            unsafe_allow_html=True
        )

        with st.expander(f"View details for Issue {idx}", expanded=False):
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(f"**Category:** {category}")
                st.markdown(f"**Why it matters:** {explanation}")
                st.markdown(f"**Future risk:** {future_risk}")

            with col_b:
                st.markdown(f"**Recommendation:** {recommendation}")
                st.markdown(f"**Impact if not fixed:** {impact}")

            if current_code:
                st.markdown("**Current Code**")
                st.code(current_code, language="python")

            if suggested_code:
                st.markdown("**Suggested Improved Code**")
                st.code(suggested_code, language="python")

            st.text_area(
                "Quick Fix Summary",
                value=f"""Issue: {title}
File: {file_name}
Function: {function_name}
Line: {line_no}
Severity: {severity}

Why:
{explanation}

Fix:
{recommendation}""",
                height=180,
                key=f"summary_{idx}"
            )

            st.download_button(
                label=f"Download Issue {idx} Details",
                data=f"""
Issue {idx}: {title}

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
                """,
                file_name=f"issue_{idx}_review.txt",
                mime="text/plain",
                key=f"download_issue_{idx}"
            )
