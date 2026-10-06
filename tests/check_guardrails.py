"""Checks the guardrails with deliberately wrong 'model output'.
Run with: python -m tests.check_guardrails"""

from datetime import date

from src.guardrails import apply_guardrails
from src.models import DeadlineStatus, MeetingAnalysis, MeetingItem, ReviewStatus

NOTES = ("Laura suggested testing next month. The team agreed to prepare example data. "
         "Tom will write the report by 2026-11-15.")

bad_owner_and_date = MeetingItem(
    id="x", type="confirmed_action", title="Prepare data", description="d",
    supporting_text="The team agreed to prepare example data.",
    owner="Laura", deadline_raw="next month",
    deadline_status="resolved", deadline_date="2026-11-01")          # model invented both

invented_quote = MeetingItem(
    id="y", type="confirmed_decision", title="Launch Friday", description="d",
    supporting_text="Everyone agreed on Friday.")                    # not in the notes

self_approved = MeetingItem(
    id="z", type="open_question", title="Test timing", description="d",
    supporting_text="Laura suggested testing next month.", status="approved")

good_item = MeetingItem(
    id="w", type="confirmed_action", title="Write report", description="d",
    supporting_text="Tom will write the report by 2026-11-15.",
    owner="Tom", deadline_raw="2026-11-15", deadline_status="none")

analysis = MeetingAnalysis(summary="s",
                           items=[bad_owner_and_date, invented_quote, self_approved, good_item])
analysis, log = apply_guardrails(analysis, NOTES, "2026-10-06")
a, b, c, d = analysis.items

assert a.owner is None and a.needs_clarification, "ambiguous 'Laura' must be cleared"
assert a.deadline_status == DeadlineStatus.NEEDS_CLARIFICATION and a.deadline_date is None
assert b.needs_clarification, "invented quote must be flagged"
assert c.status == ReviewStatus.PENDING, "self-approval must be reset"
assert d.owner == "Tom Becker" and d.deadline_status == DeadlineStatus.RESOLVED
assert d.deadline_date == date(2026, 11, 15) and not d.needs_clarification
assert [i.id for i in analysis.items] == ["item-1", "item-2", "item-3", "item-4"]

print("Corrections logged:")
for line in log:
    print(" -", line)
print("\nAll guardrail checks passed.")