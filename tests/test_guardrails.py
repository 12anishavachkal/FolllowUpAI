"""Guardrails: deliberately wrong 'model output' must be corrected and logged."""
from datetime import date

import pytest

from src.guardrails import apply_guardrails
from src.models import (DeadlineStatus, ItemType, MeetingAnalysis, MeetingItem,
                        ReviewStatus)

NOTES = ("Laura suggested testing next month. The team agreed to prepare example data. "
         "Tom will write the report by 2026-11-15. Bob will book the room.")
MEETING = "2026-10-06"


def run(item: MeetingItem) -> MeetingItem:
    analysis = MeetingAnalysis(summary="s", items=[item])
    analysis, _ = apply_guardrails(analysis, NOTES, MEETING)
    return analysis.items[0]


def make(**fields) -> MeetingItem:
    base = dict(id="x", type="confirmed_action", title="t", description="d",
                supporting_text="The team agreed to prepare example data.")
    base.update(fields)
    return MeetingItem(**base)


def test_ambiguous_owner_and_invented_date_are_corrected():
    item = run(make(owner="Laura", deadline_raw="next month",
                    deadline_status="resolved", deadline_date="2026-11-01"))
    assert item.owner is None
    assert item.needs_clarification
    assert item.deadline_status == DeadlineStatus.NEEDS_CLARIFICATION
    assert item.deadline_date is None


def test_invented_quote_is_flagged():
    item = run(make(type="confirmed_decision",
                    supporting_text="Everyone agreed on Friday."))
    assert item.needs_clarification


def test_model_cannot_self_approve():
    item = run(make(type="open_question", status="approved",
                    supporting_text="Laura suggested testing next month."))
    assert item.status == ReviewStatus.PENDING


def test_good_item_is_kept_and_canonicalised():
    item = run(make(supporting_text="Tom will write the report by 2026-11-15.",
                    owner="Tom", deadline_raw="2026-11-15"))
    assert item.owner == "Tom Becker"
    assert item.deadline_status == DeadlineStatus.RESOLVED
    assert item.deadline_date == date(2026, 11, 15)
    assert not item.needs_clarification


def test_unknown_person_is_flagged_not_trusted():
    item = run(make(supporting_text="Bob will book the room.", owner="Bob"))
    assert item.needs_clarification
    assert "team list" in item.clarification_question


def test_owner_not_in_notes_is_removed():
    item = run(make(owner="Priya Nair"))
    assert item.owner is None
    assert item.needs_clarification


def test_confirmed_action_without_owner_asks_who_owns_it():
    item = run(make(owner=None))
    assert item.needs_clarification
    assert "own" in item.clarification_question.lower()