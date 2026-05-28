import json
import os

from common.json_util import parse_json_response
from common.secrets import get_openai_api_key
from openai import OpenAI
from services.prompts import code_review_prompt


def _build_mock_review(code_input: str) -> dict:
    if not code_input or not code_input.strip():
        return {
            "success": True,
            "summary": {
                "total_issues": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_health": "Unknown",
                "text": "No code was provided for review.",
            },
            "issues": [],
            "recommendations": [],
        }
    return {
        "success": True,
        "summary": {
            "total_issues": 2,
            "high": 1,
            "medium": 1,
            "low": 0,
            "overall_health": "Moderate",
            "text": "Mock review: enable ENABLE_REAL_CODE_REVIEW for live AI analysis.",
        },
        "issues": [
            {
                "title": "Defensive checks recommended",
                "file": "uploaded_code",
                "function": "main",
                "line": 1,
                "severity": "High",
                "category": "Reliability",
                "current_code": code_input[:120],
                "explanation": "Nested access without validation.",
                "future_risk": "Runtime failures on partial API responses.",
                "recommendation": "Use .get() and explicit error handling.",
                "suggested_code": "",
                "impact": "Stability",
                "language": "unknown",
            }
        ],
        "recommendations": ["Add input validation", "Use structured logging"],
    }


def _run_ai_code_review(code_input: str) -> dict:
    client = OpenAI(api_key=get_openai_api_key(), timeout=90)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": code_review_prompt(code_input)}],
        temperature=0.2,
    )
    content = response.choices[0].message.content or ""
    parsed = parse_json_response(content)
    if "success" not in parsed:
        parsed["success"] = True
    return parsed


def run_smart_code_review(code_input: str) -> dict:
    try:
        use_real = str(os.environ.get("ENABLE_REAL_CODE_REVIEW", "true")).strip().lower() == "true"
        if use_real:
            return _run_ai_code_review(code_input)
        return _build_mock_review(code_input)
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "summary": {
                "total_issues": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_health": "Unavailable",
                "text": "Smart code review failed.",
            },
            "issues": [],
            "recommendations": [],
        }
