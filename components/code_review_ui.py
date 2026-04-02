def run_smart_code_review(code_input):
    """
    Temporary mock response for Smart Code Review.
    Replace later with real AI model call.
    """

    if not code_input or not code_input.strip():
        return {
            "summary": {
                "total_issues": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_health": "Unknown"
            },
            "issues": []
        }

    review_result = {
        "summary": {
            "total_issues": 3,
            "high": 1,
            "medium": 1,
            "low": 1,
            "overall_health": "Moderate"
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
                "impact": "Login flow may break with runtime error."
            },
            {
                "title": "Broad exception handling",
                "file": "uploaded_code.py",
                "function": "process_payment",
                "line": 28,
                "severity": "Medium",
                "category": "Maintainability",
                "current_code": "except:\n    return 'failed'",
                "explanation": "Bare except catches all exceptions and hides real root cause.",
                "future_risk": "Troubleshooting production issues will become difficult.",
                "recommendation": "Catch specific exceptions and log the real error.",
                "suggested_code": "except PaymentError as e:\n    logger.error(f'Payment failed: {e}')\n    return 'failed'",
                "impact": "Errors may be silently hidden."
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
                "recommendation": "Move config values into environment variables or config file.",
                "suggested_code": "import os\napi_url = os.getenv('API_URL', '')",
                "impact": "Environment changes will require code changes."
            }
        ]
    }

    return review_result
