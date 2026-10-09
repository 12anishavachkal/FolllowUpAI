"""Safety nets for the three known limits: model classification, review override, contradictions."""
import json
from types import SimpleNamespace

from src import analyze
from src.guardrails import apply_guardrails
from src.models import MeetingAnalysis, MeetingItem
from src.review import review_items
from src.tools.action_writer import save_approved_actions

MEETING = "2026-10-06"


def make(**fields) -> MeetingItem:
    base = dict(id="x", type="confirmed_action", title="t", description="d", supporting_text="s")
    base.update(fields)
    return MeetingItem(**base)


def run(item, notes):
    analysis, log = apply_guardrails(MeetingAnalysis(summary="s", items=[item]), notes, MEETING)
    return analysis.items[0], log


def scripted(*answers):
    answers = iter(answers)
    return lambda prompt: next(answers)


# ---- Limit 1: model classification ----
def test_confirmed_item_with_hedged_quote_is_flagged():
    notes = "The team will probably move the launch."
    item, log = run(make(type="confirmed_decision", supporting_text=notes), notes)
    assert item.needs_clarification and "probably" in item.clarification_question
    assert any("probably" in line for line in log)


def test_clean_confirmed_item_is_not_flagged():
    notes = "We decided to launch on 2026-11-02."
    item, _ = run(make(type="confirmed_decision", supporting_text=notes,
                       deadline_raw="2026-11-02"), notes)
    assert not item.needs_clarification


def test_person_who_only_suggested_is_not_the_owner():
    notes = "Tom suggested preparing the example data."
    item, log = run(make(supporting_text=notes, owner="Tom Becker"), notes)
    assert item.owner is None and item.needs_clarification
    assert any("only suggested" in line for line in log)


def test_person_who_suggests_and_will_do_it_keeps_ownership():
    notes = "Tom suggested the fix and will implement it."
    item, _ = run(make(supporting_text=notes, owner="Tom Becker"), notes)
    assert item.owner == "Tom Becker"


# ---- Limit 2: approving despite an open question needs a reason ----
def test_approve_anyway_without_reason_is_not_approved():
    item = make(needs_clarification=True, clarification_question="Who?")
    review_items([item], MEETING, ask=scripted("a", "y", "", "s"), show=lambda _: None)
    assert item.status.value == "pending" and item.approval_note is None


def test_approve_anyway_with_reason_is_saved_with_the_reason(tmp_path):
    item = make(needs_clarification=True, clarification_question="Who?")
    review_items([item], MEETING,
                 ask=scripted("a", "y", "Owner will be decided Friday"), show=lambda _: None)
    assert item.status.value == "approved"
    out = tmp_path / "o.json"
    save_approved_actions([item], str(out), "t.md")
    record = json.loads(out.read_text(encoding="utf-8"))[0]
    assert record["approval_note"] == "Owner will be decided Friday"
    assert record["needs_clarification"] is True


# ---- Limit 3: contradictions, tested without the model ----
CONTRA_NOTES = ("The team agreed that the launch will be on 2026-11-02. "
                "Later, Laura Schmidt said the launch must move to 2026-11-16.")


def _fake_agent(analysis):
    return SimpleNamespace(run_sync=lambda prompt, deps=None: SimpleNamespace(output=analysis))


def test_contradiction_is_reported_and_items_are_flagged_even_if_model_forgot(monkeypatch):
    model_answer = MeetingAnalysis(
        summary="s",
        contradictions=["The team agreed that the launch will be on 2026-11-02 but "
                        "Later, Laura Schmidt said the launch must move to 2026-11-16."],
        items=[make(type="confirmed_decision", title="Launch date", description="d",
                    supporting_text="The team agreed that the launch will be on 2026-11-02."),
               make(type="proposed_decision", title="Move launch", description="d",
                    supporting_text="Later, Laura Schmidt said the launch must move to 2026-11-16.")])
    monkeypatch.setattr(analyze, "build_agent", lambda: _fake_agent(model_answer))
    result, log = analyze.analyze_notes(CONTRA_NOTES, MEETING)
    assert len(result.contradictions) == 1
    assert all(i.needs_clarification for i in result.items)
    assert any("contradiction" in line for line in log)