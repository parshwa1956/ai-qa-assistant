import json
import os

from openai import OpenAI


def _extract_json(content: str) -> dict:
    content = (content or "").strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)


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
                "text": "No code was provided for review."
            },
            "issues": [],
            "recommendations": []
        }

    return {
        "success": True,
        "summary": {
            "total_issues": 3,
            "high": 1,
            "medium": 1,
            "low": 1,
            "overall_health": "Moderate",
            "text": "The code has a few important reliability and maintainability issues that should be fixed before production use."
        },
        "issues": [
            {
                "title": "Possible null handling issue",
                "file": "uploaded_code.py",
                "function": "login_user",
                "line": 12,
                "severity": "High",
                "category": "Reliability",
                "current_code": "token = response['data']['token']",
                "explanation": "This line assumes response, data, and token always exist.",
                "future_risk": "This may fail later if the API response changes or returns partial data.",
                "recommendation": "Add defensive checks before accessing nested values.",
                "suggested_code": "data = response.get('data', {}) if response else {}\ntoken = data.get('token')\nif not token:\n    raise ValueError('Token not found')",
                "impact": "Login flow may break with runtime error.",
                "language": "python"
            },
            {
                "title": "Broad exception handling",
                "file": "uploaded_code.py",
                "function": "process_payment",
                "line": 28,
                "severity": "Medium",
                "category": "Maintainability",
                "current_code": "except:\n    return 'failed'",
                "explanation": "Bare except catches all exceptions and hides the real root cause.",
                "future_risk": "Troubleshooting production issues will become difficult.",
                "recommendation": "Catch specific exceptions and log the real error.",
                "suggested_code": "except PaymentError as e:\n    logger.error(f'Payment failed: {e}')\n    return 'failed'",
                "impact": "Errors may be silently hidden.",
                "language": "python"
            },
            {
                "title": "Hardcoded configuration value",
                "file": "uploaded_code.py",
                "function": "module level",
                "line": 3,
                "severity": "Low",
                "category": "Configuration",
                "current_code": "api_url = 'https://prod.company.com/api/login'",
                "explanation": "The API URL is hardcoded in source code.",
                "future_risk": "Moving between dev, test, and prod environments will be harder later.",
                "recommendation": "Move config values into environment variables or a config file.",
                "suggested_code": "import os\napi_url = os.getenv('API_URL', '')",
                "impact": "Environment changes will require code changes.",
                "language": "python"
            }
        ],
        "recommendations": [
            "Add defensive null checking for nested API responses.",
            "Replace bare except blocks with specific exception handling.",
            "Move environment-specific settings into configuration."
        ]
    }


def _run_ai_code_review(code_input: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a senior software engineer performing a smart code review.

Review the code below and return ONLY valid JSON.

Use this exact structure:
{{
  "success": true,
  "summary": {{
    "total_issues": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "overall_health": "Good",
    "text": "Short overall review summary"
  }},
  "issues": [
    {{
      "title": "Issue title",
      "file": "uploaded_code.py",
      "function": "function name or module level",
      "line": 1,
      "severity": "High",
      "category": "Reliability",
      "current_code": "code snippet",
      "explanation": "Why this matters",
      "future_risk": "What may happen later",
      "recommendation": "Recommended fix",
      "suggested_code": "Improved code example",
      "impact": "Impact if not fixed",
      "language": "python"
    }}
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ]
}}

Code to review:
{code_input}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    parsed = _extract_json(content)

    if "success" not in parsed:
        parsed["success"] = True

    if "summary" not in parsed or not isinstance(parsed["summary"], dict):
        parsed["summary"] = {
            "total_issues": len(parsed.get("issues", [])),
            "high": 0,
            "medium": 0,
            "low": 0,
            "overall_health": "Unknown",
            "text": "AI review completed."
        }

    if "issues" not in parsed or not isinstance(parsed["issues"], list):
        parsed["issues"] = []

    if "recommendations" not in parsed or not isinstance(parsed["recommendations"], list):
        parsed["recommendations"] = []

    return parsed


def run_smart_code_review(code_input: str) -> dict:
    """
    Smart code review entry point.

    Default behavior:
    - Uses mock review output unless ENABLE_REAL_CODE_REVIEW=true
    - Returns a safe structured response even on failure
    """
    try:
        use_real_ai = str(os.getenv("ENABLE_REAL_CODE_REVIEW", "false")).strip().lower() == "true"

        if use_real_ai:
            return _run_ai_code_review(code_input)

        return _build_mock_review(code_input)

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": {
                "total_issues": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_health": "Unavailable",
                "text": "Smart code review service failed."
            },
            "issues": [],
            "recommendations": []
        }
