"""Summary: Owner is shown for actions (or when set), not for plain decisions."""
from src.models import MeetingItem
from src.tools.summary import render_item


def make(kind, **extra):
    return MeetingItem(id="item-1", type=kind, title="t", description="d",
                       supporting_text="s", **extra)


def test_decision_with_deadline_has_no_owner_line():
    text = render_item(make("confirmed_decision", deadline_raw="2026-11-02",
                            deadline_status="needs_clarification"))
    assert "Owner:" not in text and "Deadline:" in text


def test_action_without_owner_shows_not_assigned():
    assert "Owner: NOT ASSIGNED" in render_item(make("confirmed_action"))
