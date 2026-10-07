"""Tool: save ONLY human-approved action items to a local JSON file."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.config import load_settings
from src.models import MeetingItem, ReviewStatus


class ActionWriteError(Exception):
    """Raised when approved items cannot be saved."""


def save_approved_actions(items: list[MeetingItem], output_path: str, source_name: str) -> int:
    """Append approved action items to the JSON file and return how many were saved.

    Two safety nets apply here, even if the caller already filtered:
      * pending and rejected items are never written
      * only item types listed in settings (saving.saveable_types) are written
    """
    saveable = set(load_settings()["saving"]["saveable_types"])
    approved = [i for i in items
                if i.status == ReviewStatus.APPROVED and i.type.value in saveable]
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
    for item in approved:
        record = item.model_dump(mode="json")
        record["source_file"] = source_name
        record["saved_at"] = saved_at
        existing.append(record)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)  # write to a temp file first so a crash cannot corrupt the output
    except OSError as exc:
        raise ActionWriteError(f"Could not write output file: {exc}") from exc

    return len(approved)