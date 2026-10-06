"""Tool: check a deadline phrase. Only exact dates are accepted as resolved.

Vague phrases such as "next month" are never converted silently. They are flagged
as needing clarification, with a candidate range to help the human decide.
"""

import re
from datetime import date, datetime, timedelta

ABSOLUTE_FORMATS = ["%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%d %b %Y", "%b %d, %Y"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _result(status, resolved=None, candidate_range=None, note=""):
    return {
        "status": status,  # none | resolved | needs_clarification | error
        "date": resolved.isoformat() if resolved else None,
        "candidate_range": [d.isoformat() for d in candidate_range] if candidate_range else None,
        "note": note,
    }


def _next_month_range(today: date):
    first = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    last = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return first, last


def validate_deadline(raw_text: str, meeting_date: str) -> dict:
    """Validate a deadline phrase relative to the meeting date (YYYY-MM-DD)."""
    if not raw_text or not raw_text.strip():
        return _result("none", note="No deadline mentioned.")

    try:
        today = datetime.strptime(meeting_date, "%Y-%m-%d").date()
    except ValueError:
        return _result("error", note=f"Meeting date '{meeting_date}' is not YYYY-MM-DD.")

    text = raw_text.strip()
    lowered = text.lower()

    # 1. Exact calendar dates
    for fmt in ABSOLUTE_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt).date()
        except ValueError:
            continue
        if parsed < today:
            return _result("needs_clarification", note="This date is before the meeting date.")
        return _result("resolved", resolved=parsed, note="Exact date given.")

    # 2. Unambiguous relative words
    if lowered in ("today", "tomorrow"):
        offset = 0 if lowered == "today" else 1
        return _result("resolved", resolved=today + timedelta(days=offset),
                       note=f"'{lowered}' relative to the meeting date.")

    # 3. Vague phrases: never resolved automatically
    if "next month" in lowered:
        return _result("needs_clarification",
                       candidate_range=_next_month_range(today),
                       note="'Next month' is vague. Ask for an exact date.")
    if "next week" in lowered:
        monday = today + timedelta(days=7 - today.weekday())
        return _result("needs_clarification",
                       candidate_range=(monday, monday + timedelta(days=6)),
                       note="'Next week' is vague. Ask for an exact date.")
    match = re.search(r"\b(" + "|".join(WEEKDAYS) + r")\b", lowered)
    if match:
        target = WEEKDAYS.index(match.group(1))
        days_ahead = (target - today.weekday() - 1) % 7 + 1
        return _result("needs_clarification",
                       candidate_range=(today + timedelta(days=days_ahead),) * 2,
                       note="A weekday name is ambiguous. Confirm the exact date.")

    return _result("needs_clarification", note=f"Could not understand deadline '{raw_text}'.")