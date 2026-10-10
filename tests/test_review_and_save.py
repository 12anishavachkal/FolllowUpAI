"""Human approval: only approved items are saved. Pending, rejected and skipped never are."""
import json
from datetime import date

from src.models import MeetingItem
from src.review import review_items
from src.tools.action_writer import save_approved_actions


def make(item_id, kind, title, **extra):
    return MeetingItem(id=item_id, type=kind, title=title, description="d",
                       supporting_text="s", **extra)


def scripted(*answers):
    answers = iter(answers)
    return lambda prompt: next(answers)


def saved_titles(path):
    return {r["title"] for r in json.loads(path.read_text(encoding="utf-8"))}


def test_full_review_flow_and_saving(tmp_path):
    a = make("item-1", "confirmed_action", "Prepare data", needs_clarification=True,
             clarification_question="Who should own this action?",
             deadline_raw="next month", deadline_status="needs_clarification")
    b = make("item-2", "proposed_decision", "Test with managers",
             needs_clarification=True, clarification_question="Confirm?")
    c = make("item-3", "open_question", "External access")
    d = make("item-4", "confirmed_action", "Write report", owner="Tom Becker")

    # Item 1: ambiguous 'Laura' refused, full name accepted, 'next month' refused,
    # exact date accepted, question resolved, approved. Item 2 rejected, 3 skipped, 4 approved.
    ask = scripted("c", "Laura", "Laura Meyer", "next month", "2026-11-15", "y", "a",
                   "r", "s", "a")
    counts = review_items([a, b, c, d], "2026-10-06", ask=ask, show=lambda _: None)

    assert counts == {"approved": 2, "rejected": 1, "pending": 1}
    assert a.owner == "Laura Meyer" and a.deadline_date == date(2026, 11, 15)
    assert a.was_modified and not a.needs_clarification

    out = tmp_path / "approved.json"
    assert save_approved_actions([a, b, c, d], str(out), "t.md") == 2
    assert saved_titles(out) == {"Prepare data", "Write report"}


def test_end_of_input_approves_nothing():
    item = make("item-1", "confirmed_action", "Write report", owner="Tom Becker")

    def no_input(prompt):
        raise EOFError

    counts = review_items([item], "2026-10-06", ask=no_input, show=lambda _: None)
    assert counts["approved"] == 0


def test_unresolved_item_needs_extra_confirmation_to_approve():
    item = make("item-1", "confirmed_action", "Prepare data", needs_clarification=True,
                clarification_question="Who?")
    # 'a' then 'n' (do not approve anyway), then 's' to skip.
    review_items([item], "2026-10-06", ask=scripted("a", "n", "s"), show=lambda _: None)
    assert item.status.value == "pending"


def test_pending_and_rejected_items_are_never_written(tmp_path):
    items = [make("a", "confirmed_action", "Approved", status="approved"),
             make("b", "confirmed_action", "Pending", status="pending"),
             make("c", "confirmed_action", "Rejected", status="rejected")]
    out = tmp_path / "out.json"
    assert save_approved_actions(items, str(out), "t.md") == 1
    assert saved_titles(out) == {"Approved"}


def test_nothing_approved_creates_no_file(tmp_path):
    out = tmp_path / "out.json"
    assert save_approved_actions([make("a", "confirmed_action", "P")], str(out), "t.md") == 0
    assert not out.exists()


def test_saved_records_carry_source_and_timestamp(tmp_path):
    out = tmp_path / "out.json"
    save_approved_actions([make("a", "confirmed_action", "A", status="approved")],
                          str(out), "clear_notes.md")
    record = json.loads(out.read_text(encoding="utf-8"))[0]
    assert record["source_file"] == "clear_notes.md" and record["saved_at"]


def test_only_action_types_are_saved(tmp_path):
    """Requires the 'saveable_types' setting from the action-only saving change."""
    items = [make("a", "confirmed_action", "An action", status="approved"),
             make("b", "open_question", "A question", status="approved")]
    out = tmp_path / "out.json"
    assert save_approved_actions(items, str(out), "t.md") == 1
    assert saved_titles(out) == {"An action"}

def test_changing_owner_updates_old_name_in_description_but_not_quote():
    item = MeetingItem(id="item-1", type="confirmed_action",
                       title="Tom Becker writes report",
                       description="Tom Becker will write the report.",
                       supporting_text="Tom will write the report.",
                       owner="Tom Becker")
    # m = modify; Enter keeps title and description; new owner 'Priya'; Enter keeps
    # the deadline; r = reject to leave the item.
    ask = scripted("m", "", "", "Priya", "", "r")
    review_items([item], "2026-10-06", ask=ask, show=lambda _: None)

    assert item.owner == "Priya Nair"
    assert "Tom" not in item.title and "Tom" not in item.description
    assert "Priya Nair" in item.description
    assert item.supporting_text == "Tom will write the report."  # original quote kept

def test_same_approved_item_is_not_saved_twice(tmp_path):
    out = tmp_path / "o.json"
    item = make("item-1", "confirmed_action", "Write report", owner="Tom Becker",
                status="approved")
    assert save_approved_actions([item], str(out), "notes.md") == 1
    assert save_approved_actions([item], str(out), "notes.md") == 0   # duplicate skipped
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 1
    assert save_approved_actions([item], str(out), "other.md") == 1   # other source is new


def test_save_returns_only_new_count_when_some_are_duplicates(tmp_path):
    """Regression: a mix of already-saved and new items must report only the new ones."""
    out = tmp_path / "o.json"
    first = make("a", "confirmed_action", "A", status="approved")
    assert save_approved_actions([first], str(out), "t.md") == 1
    again = make("a", "confirmed_action", "A", status="approved")
    fresh = make("b", "confirmed_action", "B", status="approved")
    assert save_approved_actions([again, fresh], str(out), "t.md") == 1
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 2
