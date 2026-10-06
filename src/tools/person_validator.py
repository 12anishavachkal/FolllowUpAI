"""Tool: check a name or role against the fictional team list in config/team.json."""

import json

from src.config import load_settings, resolve_path


class TeamFileError(Exception):
    """Raised when the team file is missing or invalid."""


def _load_team() -> dict:
    path = resolve_path(load_settings()["paths"]["team_file"])
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TeamFileError(f"Cannot load team file {path}: {exc}") from exc


def _singular(word: str) -> str:
    return word[:-1] if word.endswith("s") else word


def validate_person(name_or_role: str) -> dict:
    """Return whether a name or role is a known, unambiguous team member or role."""
    query = (name_or_role or "").strip().lower()
    if not query:
        return {"status": "none", "query": name_or_role, "matches": [], "note": "No name given."}

    team = _load_team()

    # Role match, e.g. "project managers" -> "Project Manager"
    for role in team["roles"]:
        if _singular(query) == role.lower():
            members = [p for p in team["people"] if p["role"] == role]
            return {"status": "role", "query": name_or_role, "matches": members,
                    "note": f"'{role}' is a role, not a single person."}

    # Name match: every word in the query must appear in the person's name
    tokens = query.split()
    matches = [p for p in team["people"]
               if all(t in p["name"].lower().split() for t in tokens)]

    if len(matches) == 1:
        return {"status": "found", "query": name_or_role, "matches": matches, "note": "Known team member."}
    if len(matches) > 1:
        return {"status": "ambiguous", "query": name_or_role, "matches": matches,
                "note": "Several people match. Ask which one."}
    return {"status": "unknown", "query": name_or_role, "matches": [],
            "note": "Not in the team list. Do not assign."}