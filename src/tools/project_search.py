"""Tool: look up facts about the fictional project in config/project_info.json.

The agent may use this to check a project term before describing it. If nothing is
found, the agent must say so and must NOT invent a project fact.
"""

import json
import re

from src.config import load_settings, resolve_path


class ProjectInfoError(Exception):
    """Raised when the project-information file is missing or invalid."""


def _load_facts() -> list[dict]:
    path = resolve_path(load_settings()["paths"]["project_info_file"])
    try:
        return json.loads(path.read_text(encoding="utf-8"))["facts"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise ProjectInfoError(f"Cannot load project information {path}: {exc}") from exc


def search_project_info(query: str) -> dict:
    """Return the fictional project facts whose topic or keywords match the query."""
    words = {w for w in re.findall(r"[a-z0-9]+", (query or "").lower()) if len(w) > 2}
    if not words:
        return {"status": "none", "query": query, "matches": [],
                "note": "Empty query. No project fact available."}

    matches = []
    for entry in _load_facts():
        vocab = set(entry["keywords"]) | set(re.findall(r"[a-z0-9]+", entry["topic"].lower()))
        if words & vocab:
            matches.append({"topic": entry["topic"], "fact": entry["fact"]})

    if not matches:
        return {"status": "none", "query": query, "matches": [],
                "note": "No project fact found. Do not invent one."}
    return {"status": "found", "query": query, "matches": matches,
            "note": "Facts from the fictional project file."}
