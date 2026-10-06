"""Checks the review loop with scripted answers (no typing, no API call).
Run with: python -m tests.check_review"""

import json
import tempfile
from datetime import date
from pathlib import Path

from src.models import MeetingItem
from src.review import review_items
from src.tools.action_writer import save_approved_actions


def make(item_id, kind, title, **extra):
    return MeetingItem(id=item_id, type=kind, title=title, description="d",
                       supporting_text="s", **extra)


a = make("item-1", "confirmed_action", "Prepare data", needs_clarification=True,
         clarification_question="Who should own this action?",
         deadline_raw="next month", deadline_status="needs_clarification")
b = make("item-2", "proposed_decision", "Test with managers",
         needs_clarification=True, clarification_question="Confirm?")
c = make("item-3", "open_question", "External access")
d = make("item-4", "confirmed_action", "Write report", owner="Tom Becker")

# Item 1: complete (ambiguous 'Laura' refused, then full name; 'next month' refused,
#         then exact date), mark resolved, approve.  Item 2: reject.
# Item 3: skip.  Item 4: approve.
answers = iter(["c", "Laura", "Laura Meyer", "next month", "2026-11-15", "y", "a",
                "r", "s", "a"])
counts = review_items([a, b, c, d], "2026-10-06", ask=lambda prompt: next(answers), show=print)

assert counts == {"approved": 2, "rejected": 1, "pending": 1}, counts
assert a.owner == "Laura Meyer" and a.deadline_date == date(2026, 11, 15)
assert a.was_modified and not a.needs_clarification

with tempfile.TemporaryDirectory() as folder:
    out = Path(folder) / "approved.json"
    saved = save_approved_actions([a, b, c, d], str(out), "check.md")
    titles = {r["title"] for r in json.loads(out.read_text(encoding="utf-8"))}

assert saved == 2 and titles == {"Prepare data", "Write report"}, titles
print("\nAll review checks passed. Only approved items were saved:", sorted(titles))