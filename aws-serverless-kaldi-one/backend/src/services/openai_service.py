import base64
import os
import time
from typing import Any, Optional

from openai import OpenAI

from common.json_util import parse_json_response
from common.secrets import get_openai_api_key
from services import prompts

MAX_CONTEXT_CHARS = 15000
OPENAI_TIMEOUT = 90
MAX_RETRIES = 2


def _client() -> OpenAI:
    return OpenAI(api_key=get_openai_api_key(), timeout=OPENAI_TIMEOUT)


def _truncate(text: str, limit: int = MAX_CONTEXT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def _chat(prompt: str, image_data_url: Optional[str] = None) -> str:
    client = _client()
    messages: list[dict[str, Any]]
    if image_data_url:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        ]
    else:
        messages = [{"role": "user", "content": prompt}]

    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2 if "code review" in prompt.lower() else None,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            last_err = exc
            if attempt < MAX_RETRIES and _is_retryable(exc):
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise last_err or RuntimeError("OpenAI request failed")


def _is_retryable(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    return "timeout" in name or "rate" in msg or "503" in msg or "502" in msg


def image_to_data_url(content_type: str, raw: bytes) -> str:
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:{content_type};base64,{b64}"


def _records_to_table(records: list[dict]) -> list[dict]:
    return records


def _format_bug_report(parsed: dict) -> tuple[str, list[dict], dict]:
    bug = parsed["bug_report"]
    pretty = "\n".join(f"{k}: {v}" for k, v in bug.items())
    return pretty, [bug], parsed


def _format_list_records(parsed: dict, key: str, formatter) -> tuple[str, list[dict], dict]:
    records = parsed[key]
    pretty = formatter(records)
    return pretty, _records_to_table(records), parsed


def generate(
    workspace: str,
    output_type: str,
    title: str,
    context: str,
    *,
    image_bytes: Optional[bytes] = None,
    image_content_type: Optional[str] = None,
    source_filename: str = "",
    code_input: str = "",
) -> dict[str, Any]:
    context = _truncate(context)
    title = (title or "Untitled").strip()
    image_url = None
    if image_bytes and image_content_type:
        image_url = image_to_data_url(image_content_type, image_bytes)

    if output_type == "Smart Code Review":
        from services.code_review_service import run_smart_code_review

        result = run_smart_code_review(code_input or context)
        return {
            "outputType": output_type,
            "outputText": result.get("summary", {}).get("text", "Code review complete"),
            "outputJson": result,
            "tableData": [],
            "mermaidCode": None,
        }

    if workspace == "qa":
        return _generate_qa(output_type, title, context, image_url)
    if workspace == "ba":
        return _generate_ba(output_type, title, context, source_filename)
    if workspace == "dev":
        return _generate_dev(output_type, title, context)
    if workspace == "flow":
        return _generate_flow(output_type, title, context, image_url)
    raise ValueError(f"Unknown workspace: {workspace}")


def _generate_qa(output_type: str, title: str, context: str, image_url: Optional[str]) -> dict:
    if output_type == "Bug Report":
        prompt = prompts.bug_report_prompt(title, context)
        content = _chat(prompt, image_url)
        parsed = parse_json_response(content)
        pretty, table, raw = _format_bug_report(parsed)
    elif output_type == "Test Cases":
        prompt = prompts.test_cases_prompt(title, context)
        content = _chat(prompt, image_url)
        parsed = parse_json_response(content)
        records = parsed["test_cases"]

        def fmt(recs):
            blocks = []
            for tc in recs:
                blocks.append(
                    "\n".join(
                        f"{k}: {tc.get(k, '')}"
                        for k in [
                            "Test Case ID",
                            "Category",
                            "Scenario",
                            "Preconditions",
                            "Steps",
                            "Expected Result",
                            "Priority",
                            "Type",
                        ]
                    )
                )
            return "\n" + ("\n" + "-" * 80 + "\n").join(blocks)

        pretty, table, raw = _format_list_records(parsed, "test_cases", fmt)
    elif output_type == "Test Scenarios":
        prompt = prompts.test_scenarios_prompt(title, context)
        content = _chat(prompt, image_url)
        parsed = parse_json_response(content)
        records = parsed["test_scenarios"]
        pretty = "\n".join(
            f"Scenario ID: {s.get('Scenario ID','')}\nScenario: {s.get('Scenario','')}" for s in records
        )
        table, raw = _records_to_table(records), parsed
    else:
        raise ValueError(f"Unsupported QA output type: {output_type}")

    return {
        "outputType": output_type,
        "outputText": pretty,
        "outputJson": raw,
        "tableData": table,
        "mermaidCode": None,
    }


def _generate_ba(output_type: str, title: str, context: str, source_filename: str) -> dict:
    if output_type in ("Business Process Flow", "Data Flow Diagram"):
        prompt = prompts.flow_diagram_prompt(title, context, output_type)
        content = _chat(prompt)
        parsed = parse_json_response(content)
        diagram = parsed["diagram_output"]
        mermaid = diagram.get("mermaid_code", "")
        steps = diagram.get("steps", [])
        pretty = f"Diagram Type: {diagram.get('diagram_type', output_type)}\n\nMermaid Code:\n{mermaid}"
        return {
            "outputType": output_type,
            "outputText": pretty,
            "outputJson": parsed,
            "tableData": steps,
            "mermaidCode": mermaid,
        }

    if output_type == "User Story + Acceptance Criteria + Traceability":
        prompt = prompts.traceability_prompt(title, context, source_filename)
        content = _chat(prompt)
        parsed = parse_json_response(content)
        stories = parsed.get("stories", [])
        rows = []
        blocks = []
        for s in stories:
            ac = s.get("Acceptance Criteria", [])
            ac_text = "\n".join(f"- {x}" for x in ac) if isinstance(ac, list) else str(ac)
            trace = s.get("Traceability", []) or []
            trace_text = "\n".join(
                f"Source: {t.get('Source Section','')} | {t.get('Source Excerpt','')}" for t in trace
            )
            blocks.append(
                f"User Story ID: {s.get('User Story ID','')}\nStory Title: {s.get('Story Title','')}\n{ac_text}\n{trace_text}"
            )
            rows.append(
                {
                    "User Story ID": s.get("User Story ID", ""),
                    "Story Title": s.get("Story Title", ""),
                    "As a": s.get("As a", ""),
                    "I want": s.get("I want", ""),
                    "So that": s.get("So that", ""),
                    "Priority": s.get("Priority", ""),
                    "Acceptance Criteria": ac_text,
                    "Traceability Details": trace_text,
                }
            )
        return {
            "outputType": output_type,
            "outputText": "\n\n".join(blocks),
            "outputJson": parsed,
            "tableData": rows,
            "mermaidCode": None,
        }

    prompt = prompts.ba_prompt(title, context, output_type)
    content = _chat(prompt)
    parsed = parse_json_response(content)
    key_map = {
        "Requirement to User Story": "user_stories",
        "Acceptance Criteria Generator": "acceptance_criteria",
        "Business Requirement Breakdown": "requirement_breakdown",
    }
    key = key_map[output_type]
    records = parsed[key]
    pretty = "\n\n".join(str(r) for r in records)
    return {
        "outputType": output_type,
        "outputText": pretty,
        "outputJson": parsed,
        "tableData": records,
        "mermaidCode": None,
    }


def _generate_dev(output_type: str, title: str, context: str) -> dict:
    if output_type == "Technical Flow Diagram":
        prompt = prompts.flow_diagram_prompt(title, context, output_type)
        content = _chat(prompt)
        parsed = parse_json_response(content)
        diagram = parsed["diagram_output"]
        mermaid = diagram.get("mermaid_code", "")
        steps = diagram.get("steps", [])
        pretty = f"Diagram Type: {diagram.get('diagram_type', output_type)}\n\nMermaid Code:\n{mermaid}"
        return {
            "outputType": output_type,
            "outputText": pretty,
            "outputJson": parsed,
            "tableData": steps,
            "mermaidCode": mermaid,
        }

    prompt = prompts.dev_prompt(title, context, output_type)
    content = _chat(prompt)
    parsed = parse_json_response(content)
    key_map = {
        "Technical Task Breakdown": "technical_tasks",
        "API / Backend Tasks": "api_tasks",
        "Developer Checklist": "developer_checklist",
    }
    key = key_map[output_type]
    records = parsed[key]
    return {
        "outputType": output_type,
        "outputText": "\n\n".join(str(r) for r in records),
        "outputJson": parsed,
        "tableData": records,
        "mermaidCode": None,
    }


def _generate_flow(output_type: str, title: str, context: str, image_url: Optional[str]) -> dict:
    prompt = prompts.flow_requirements_prompt()
    full_prompt = f"{prompt}\n\nTitle: {title}\nContext: {context}"
    content = _chat(full_prompt, image_url)
    parsed = parse_json_response(content)
    req = parsed.get("requirements", parsed)
    pretty_lines = [f"Process Summary: {req.get('Process Summary', '')}"]
    for section in [
        "What Happens from Start to Finish",
        "Important Decisions",
        "Test Data Needed",
    ]:
        items = req.get(section, [])
        if items:
            pretty_lines.append(f"\n{section}:")
            pretty_lines.extend(f"- {x}" for x in items)
    return {
        "outputType": output_type,
        "outputText": "\n".join(pretty_lines),
        "outputJson": parsed,
        "tableData": [],
        "mermaidCode": None,
    }
