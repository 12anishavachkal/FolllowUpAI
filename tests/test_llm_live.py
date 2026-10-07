"""Live model checks. Skipped unless RUN_LLM_TESTS=1 (they use the real API).

Gemini's wording varies between runs, so these test RULES, not exact text.
"""
import os
from pathlib import Path

import pytest

from src.analyze import analyze_notes
from src.models import DeadlineStatus, ItemType, ReviewStatus

pytestmark = pytest.mark.skipif(os.getenv("RUN_LLM_TESTS") != "1",
                                reason="live model test; set RUN_LLM_TESTS=1 to run")

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
MEETING = "2026-10-06"


def analyse(name):
    text = (SAMPLES / name).read_text(encoding="utf-8-sig")
    analysis, _ = analyze_notes(text, MEETING)
    return analysis


def test_clear_notes_are_extracted_without_clarification_noise():
    analysis = analyse("clear_notes.md")
    actions = [i for i in analysis.items if i.type == ItemType.CONFIRMED_ACTION]
    assert len(actions) >= 3
    assert all(i.owner for i in actions)
    assert all(i.deadline_status == DeadlineStatus.RESOLVED for i in actions)
    assert all(i.status == ReviewStatus.PENDING for i in analysis.items)


def test_assignment_example_keeps_uncertainty():
    analysis = analyse("example_pdf.md")
    items = analysis.items
    text = lambda i: f"{i.title} {i.description}".lower()
    assert not any(i.owner and "laura" in i.owner.lower() for i in items)
    assert any(i.type == ItemType.PROPOSED_DECISION for i in items)
    assert any(i.type == ItemType.OPEN_QUESTION and "external" in text(i) for i in items)
    assert any(i.type == ItemType.CONFIRMED_ACTION and "data" in text(i) and not i.owner
               for i in items)
    assert any(i.deadline_status == DeadlineStatus.NEEDS_CLARIFICATION for i in items)


def test_contradictions_are_reported_not_resolved():
    analysis = analyse("contradictory_notes.md")
    assert len(analysis.contradictions) >= 1
    assert any(i.needs_clarification for i in analysis.items)