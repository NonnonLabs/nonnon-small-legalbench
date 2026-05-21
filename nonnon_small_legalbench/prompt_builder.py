from __future__ import annotations

import re
from pathlib import Path

import requests


LEGALBENCH_RAW = "https://raw.githubusercontent.com/HazyResearch/legalbench/main/tasks/{task}/base_prompt.txt"


def _cache_path(task: str) -> Path:
    return Path(".cache") / "prompts" / f"{task}.txt"


def load_base_prompt(task: str) -> str:
    path = _cache_path(task)
    if path.exists():
        return path.read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    url = LEGALBENCH_RAW.format(task=task)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    text = response.text
    path.write_text(text, encoding="utf-8")
    return text


def render_prompt(template: str, row: dict[str, object]) -> str:
    rendered = str(template)
    for key, value in row.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"{{\s*([^{}]+)\s*}}", rendered)))
    if unresolved:
        fields = ", ".join(unresolved)
        raise ValueError(f"unresolved prompt fields: {fields}")
    return rendered
