import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

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

st.title("AI QA Assistant")
st.write("Generate bug reports, test cases, and high-level test scenarios using AI.")

title = st.text_input("Title / Requirement / Feature")
context = st.text_area("Context / Business Requirement Details")

if st.button("Generate Bug Report"):
    prompt = f"""
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

Keep it practical, realistic, and ready to copy into Jira or Azure DevOps.
If some details are missing, make reasonable QA assumptions.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.subheader("Generated Bug Report")
    st.write(response.choices[0].message.content)
if not title:
    st.warning("Please enter a title or requirement before generating results.")
if st.button("Generate Test Cases"):
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

    st.subheader("Generated Test Cases")
    st.write(response.choices[0].message.content)

if st.button("Generate Test Scenarios"):
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

    st.subheader("Generated Test Scenarios")
    st.write(response.choices[0].message.content)
