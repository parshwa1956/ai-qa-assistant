import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.json_util import parse_json_response


def test_parse_json_with_markdown_fence():
    raw = '```json\n{"test_cases": [{"Test Case ID": "TC_001"}]}\n```'
    parsed = parse_json_response(raw)
    assert "test_cases" in parsed
    assert parsed["test_cases"][0]["Test Case ID"] == "TC_001"


def test_parse_json_embedded():
    raw = 'Here is output:\n{"bug_report": {"Title": "Bug"}}\nThanks'
    parsed = parse_json_response(raw)
    assert parsed["bug_report"]["Title"] == "Bug"
