"""Date validator: only exact dates resolve; vague wording is never converted silently."""
import pytest

from src.tools.date_validator import validate_deadline

MEETING = "2026-10-06"


def test_exact_date_resolves():
    result = validate_deadline("2026-11-15", MEETING)
    assert result["status"] == "resolved"
    assert result["date"] == "2026-11-15"


@pytest.mark.parametrize("text", ["15 November 2026", "November 15, 2026"])
def test_other_exact_formats_resolve(text):
    assert validate_deadline(text, MEETING)["date"] == "2026-11-15"


def test_next_month_needs_clarification_with_candidate_range():
    result = validate_deadline("next month", MEETING)
    assert result["status"] == "needs_clarification"
    assert result["date"] is None
    assert result["candidate_range"] == ["2026-11-01", "2026-11-30"]


@pytest.mark.parametrize("text", ["next week", "Friday", "soon"])
def test_other_vague_wording_is_never_resolved(text):
    result = validate_deadline(text, MEETING)
    assert result["status"] == "needs_clarification"
    assert result["date"] is None


def test_today_and_tomorrow_resolve():
    assert validate_deadline("today", MEETING)["date"] == "2026-10-06"
    assert validate_deadline("tomorrow", MEETING)["date"] == "2026-10-07"


def test_date_before_meeting_is_flagged():
    assert validate_deadline("2026-09-01", MEETING)["status"] == "needs_clarification"


def test_empty_text_means_no_deadline():
    assert validate_deadline("", MEETING)["status"] == "none"


def test_bad_meeting_date_is_an_error():
    assert validate_deadline("2026-11-15", "06/10/2026")["status"] == "error"

def test_next_friday_gives_both_possible_dates():
    result = validate_deadline("next Friday", MEETING)   # 2026-10-06 is a Tuesday
    assert result["status"] == "needs_clarification" and result["date"] is None
    assert result["candidate_range"] == ["2026-10-09", "2026-10-16"]
