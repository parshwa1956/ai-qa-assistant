import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI QA Assistant")

title = st.text_input("Bug Title")
context = st.text_area("Optional Context")

if st.button("Generate Bug Report"):
    prompt = f"""
You are a senior QA engineer.

Generate a professional bug report.

Bug Title: {title}
Context: {context}

Return:
Title
Description
Steps to reproduce
Expected result
Actual result
Severity
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.write(response.choices[0].message.content)


if st.button("Generate Test Cases"):
    prompt = f"""
Generate QA test cases for this issue.

Bug Title: {title}
Context: {context}

Return:
Functional test cases
Negative test cases
Edge cases
Regression tests
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.write(response.choices[0].message.content)
