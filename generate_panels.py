import json
import re

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate

template = """
You are a cartoon creator.

Return ONLY valid JSON in this shape:
{"panels":[{"number":1,"description":"comma-separated visual description","text":"short dialogue"}]}

Create six panels from the scenario. Repeat the complete physical description of every visible character in each panel. Keep text short. Do not use markdown fences or commentary.

Scenario:
{scenario}
"""


def generate_panels(scenario):
    model = ChatOpenAI(model_name="gpt-4")
    prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(template)
    ])
    result = model(prompt.format_messages(scenario=scenario))
    panels = extract_panel_info(result.content)
    if not panels:
        raise ValueError("The model returned no valid panels.")
    return panels


def _normalize_panels(value):
    if isinstance(value, dict):
        value = value.get("panels", [])
    if not isinstance(value, list):
        return []

    panels = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        description = str(item.get("description", "")).strip()
        text = str(item.get("text", "")).strip()
        if not description:
            continue
        number = item.get("number", index)
        try:
            number = int(number)
        except (TypeError, ValueError):
            number = index
        panels.append({
            "number": number,
            "description": description,
            "text": text,
        })
    return panels


def extract_panel_info(text):
    """Parse JSON first, then support the legacy markdown format as a safe fallback."""
    raw = text.strip()

    candidates = [raw]
    fenced = re.search(r"\x60\x60\x60(?:json)?\s*(.*?)\s*\x60\x60\x60", raw, re.IGNORECASE | re.DOTALL)
    if fenced:
        candidates.insert(0, fenced.group(1))

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        candidates.append(raw[start:end + 1])

    for candidate in candidates:
        try:
            panels = _normalize_panels(json.loads(candidate))
            if panels:
                return panels
        except json.JSONDecodeError:
            pass

    legacy = []
    blocks = re.split(r"(?im)^\s*#\s*Panel\s+", raw)
    for index, block in enumerate(blocks, start=1):
        if not block.strip():
            continue
        number_match = re.match(r"(\d+)", block.strip())
        description_match = re.search(r"(?im)^\s*description:\s*(.+)$", block)
        text_match = re.search(
            r"(?is)^\s*text:\s*(?:\x60\x60\x60(?:text)?\s*)?(.*?)(?:\x60\x60\x60|$)",
            block,
        )
        description = description_match.group(1).strip() if description_match else ""
        panel_text = text_match.group(1).strip() if text_match else ""
        if description:
            legacy.append({
                "number": int(number_match.group(1)) if number_match else index,
                "description": description,
                "text": panel_text,
            })
    return legacy
