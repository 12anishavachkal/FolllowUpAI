"""Tool: save ONLY human-approved items of the configured types to a local JSON file."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.config import load_settings
from src.models import ItemType, MeetingItem, ReviewStatus


class ActionWriteError(Exception):
    """Raised when approved items cannot be saved."""


def saveable_types() -> set[str]:
    """Item types that may be saved (config/settings.yaml, output.saveable_types).

    If the setting is missing, every item type may be saved.
    """
    configured = (load_settings().get("output") or {}).get("saveable_types")
    return set(configured) if configured else {t.value for t in ItemType}


DUPLICATE_KEY_FIELDS = ("source_file", "type", "title", "owner", "deadline_date",
                        "supporting_text")


def _duplicate_key(record: dict) -> tuple:
    """Identify a record by its content, ignoring status and save time."""
    return tuple(record.get(field) for field in DUPLICATE_KEY_FIELDS)


def save_approved_actions(items: list[MeetingItem], output_path: str, source_name: str) -> int:
    """Append approved items of a saveable type to the JSON file; return how many were NEW.

    An item already in the file (same source, type, title, owner, deadline and quote)
    is skipped, so running the same notes twice does not create duplicates.

    Items that are pending, rejected or of another type are filtered out here as a
    second safety net, even if the caller already filtered them.
    """
    allowed = saveable_types()
    approved = [i for i in items
                if i.status == ReviewStatus.APPROVED and i.type.value in allowed]
    if not approved:
        return 0

    path = Path(output_path)
    existing: list = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ActionWriteError(f"Existing output file is unreadable: {exc}") from exc
        if not isinstance(existing, list):
            raise ActionWriteError("Existing output file has an unexpected format.")

    saved_at = datetime.now(timezone.utc).isoformat()
    known = {_duplicate_key(r) for r in existing if isinstance(r, dict)}
    new_count = 0
    for item in approved:
        record = item.model_dump(mode="json")
        record["source_file"] = source_name
        record["saved_at"] = saved_at
        if _duplicate_key(record) in known:
            continue
        known.add(_duplicate_key(record))
        existing.append(record)
        new_count += 1

    if new_count == 0:
        return 0

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)  # write to a temp file first so a crash cannot corrupt the output
    except OSError as exc:
        raise ActionWriteError(f"Could not write output file: {exc}") from exc

    return len(approved)