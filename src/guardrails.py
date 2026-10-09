"""Deterministic safety net that runs AFTER the model answers.

The model can still make mistakes, so this code re-checks its output:
  * every item is forced back to 'pending' (only a human can approve)
  * quoted evidence must really appear in the notes
  * owners must appear in the notes and pass the person validator
  * deadlines are re-validated by the date tool and override the model's claim
Every change is logged so the user can see what was corrected.
"""

import re
from datetime import date

from src.models import DeadlineStatus, ItemType, MeetingAnalysis, MeetingItem, ReviewStatus
from src.tools.date_validator import validate_deadline
from src.tools.person_validator import validate_person

# Wording that signals "not agreed". A confirmed item whose own quote contains one of
# these is flagged (not re-typed: the human decides).
HEDGE_PATTERN = re.compile(
    r"\b(probably|maybe|perhaps|possibly|might|could|should consider|should probably|"
    r"suggest(?:ed|s)?|propos(?:ed|es?)|recommend(?:ed|s)?|wonder(?:ed|s)?|not sure|"
    r"tentative(?:ly)?)\b", re.IGNORECASE)
# The person only voiced an idea: "Laura suggested ...", "Tom asked whether ..."
IDEA_VERBS = (r"(?:suggest(?:ed|s)?|propos(?:ed|es?)|recommend(?:ed|s)?|ask(?:ed|s)?|"
              r"wonder(?:ed|s)?|mention(?:ed|s)?|raise[ds]?|ask(?:ed)? whether|thought)")
CONFIRMED_TYPES = (ItemType.CONFIRMED_DECISION, ItemType.CONFIRMED_ACTION)


def _words(text: str) -> str:
    """Lowercase, drop punctuation and markdown, collapse spaces (forgiving comparison)."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def _flag(item: MeetingItem, question: str) -> None:
    """Mark an item as needing clarification and add the question."""
    item.needs_clarification = True
    if not item.clarification_question:
        item.clarification_question = question
    elif question not in item.clarification_question:
        item.clarification_question += " " + question


def _check_owner(item: MeetingItem, label: str, notes_flat: str,
                 notes_vocab: set[str], log: list[str]) -> None:
    if not item.owner:
        return
    written = item.owner
    phrase = _words(written)

    # Use only the part of the owner that the notes really contain. If the notes
    # say "Laura" and the model wrote "Laura Meyer", we validate "laura", so the
    # validator sees both Lauras and the owner is NOT silently chosen by the model.
    if f" {phrase}" in f" {notes_flat}":
        checked = written
    else:
        in_notes = [t for t in phrase.split() if t in notes_vocab]
        if not in_notes:
            item.owner = None
            _flag(item, "Who is responsible for this? No owner is named in the notes.")
            log.append(f"{label}: owner '{written}' does not appear in the notes; removed.")
            return
        checked = " ".join(in_notes)

    result = validate_person(checked)
    status = result["status"]
    if status == "found":
        canonical = result["matches"][0]["name"]
        if canonical != written:
            item.owner = canonical
            log.append(f"{label}: owner '{written}' matched to team member '{canonical}'.")
    elif status == "ambiguous":
        names = ", ".join(m["name"] for m in result["matches"])
        item.owner = None
        _flag(item, f"Which person is meant by '{checked}'? Possible: {names}.")
        log.append(f"{label}: owner '{written}' matches several people; removed.")
    elif status == "role":
        _flag(item, f"'{written}' is a role, not a person. Who exactly is responsible?")
        log.append(f"{label}: owner '{written}' is a role; flagged.")
    else:
        _flag(item, f"'{written}' is not in the team list. Please confirm the owner.")
        log.append(f"{label}: owner '{written}' is not in the team list; flagged.")

def _set_no_deadline(item: MeetingItem) -> None:
    item.deadline_raw = None
    item.deadline_status = DeadlineStatus.NONE
    item.deadline_date = None


def _check_deadline(item: MeetingItem, label: str, notes_flat: str,
                    meeting_date: str, log: list[str]) -> None:
    before = (item.deadline_status, item.deadline_date)
    raw = (item.deadline_raw or "").strip()

    if not raw:
        _set_no_deadline(item)
        if before != (DeadlineStatus.NONE, None):
            log.append(f"{label}: model gave a deadline but no wording from the notes; removed.")
        return

    if _words(raw) not in notes_flat:
        _set_no_deadline(item)
        log.append(f"{label}: deadline wording '{raw}' not found in the notes; removed.")
        return

    check = validate_deadline(raw, meeting_date)
    if check["status"] == "resolved":
        item.deadline_status = DeadlineStatus.RESOLVED
        item.deadline_date = date.fromisoformat(check["date"])
    elif check["status"] == "none":
        _set_no_deadline(item)
    else:
        item.deadline_status = DeadlineStatus.NEEDS_CLARIFICATION
        item.deadline_date = None
        question = f"What is the exact deadline for '{raw}'?"
        window = check["candidate_range"]
        if window and window[0] != window[1]:
            question += f" It could fall between {window[0]} and {window[1]}."
        _flag(item, question)

    if before != (item.deadline_status, item.deadline_date):
        log.append(f"{label}: deadline '{raw}' re-checked by the date validator "
                   f"(now {item.deadline_status.value}).")


def _check_hedging(item: MeetingItem, label: str, log: list[str]) -> None:
    """A 'confirmed' item whose quote sounds hedged must be confirmed by a human."""
    if item.type not in CONFIRMED_TYPES:
        return
    hit = HEDGE_PATTERN.search(item.supporting_text)
    if hit:
        _flag(item, f"The notes say '{hit.group(0)}', which sounds undecided. "
                    "Was this really agreed?")
        log.append(f"{label}: marked '{item.type.value}' but the quote contains "
                   f"'{hit.group(0)}'; flagged for confirmation.")


def _check_idea_only_owner(item: MeetingItem, label: str, log: list[str]) -> None:
    """Remove an owner who only appears as the person who suggested or asked."""
    if not item.owner:
        return
    names = {item.owner.lower(), *item.owner.lower().split()}
    quote = item.supporting_text
    for name in names:
        if re.search(rf"\b{re.escape(name)}\b\s+{IDEA_VERBS}\b", quote, re.IGNORECASE):
            if re.search(rf"\b{re.escape(name)}\b.*?\b(?:will|agreed to|is going to|"
                         rf"takes?|owns?|volunteer(?:ed|s)?)\b", quote, re.IGNORECASE):
                return  # the same quote also gives them the task
            written, item.owner = item.owner, None
            _flag(item, f"{written} only suggested or raised this. Who is responsible?")
            log.append(f"{label}: owner '{written}' only suggested or asked in the quote; removed.")
            return


def _flag_contradictions(analysis: MeetingAnalysis, log: list[str]) -> None:
    """Items quoted inside a reported contradiction must be flagged, whatever the model did."""
    for text in analysis.contradictions:
        flat = _words(text)
        for number, item in enumerate(analysis.items, start=1):
            quote = _words(item.supporting_text)
            if quote and quote in flat and not item.needs_clarification:
                _flag(item, "This statement contradicts another part of the notes. "
                            "Which version is correct?")
                log.append(f"item-{number}: part of a contradiction; flagged.")


def apply_guardrails(analysis: MeetingAnalysis, notes_text: str,
                     meeting_date: str) -> tuple[MeetingAnalysis, list[str]]:
    """Correct the model's output in place. Returns (analysis, list of corrections)."""
    notes_flat = _words(notes_text)
    notes_vocab = set(notes_flat.split())
    log: list[str] = []

    for number, item in enumerate(analysis.items, start=1):
        label = f"item-{number}"
        item.id = label

        if item.status != ReviewStatus.PENDING:
            log.append(f"{label}: model set status '{item.status.value}'; reset to pending.")
        item.status = ReviewStatus.PENDING
        item.was_modified = False

        if _words(item.supporting_text) not in notes_flat:
            _flag(item, "The quoted source text was not found in the notes. "
                        "Please check this item against the original notes.")
            log.append(f"{label}: supporting text is not word for word in the notes; flagged.")

        _check_hedging(item, label, log)
        _check_owner(item, label, notes_flat, notes_vocab, log)
        _check_idea_only_owner(item, label, log)
        _check_deadline(item, label, notes_flat, meeting_date, log)

        if item.type == ItemType.CONFIRMED_ACTION and not item.owner:
            _flag(item, "Who should own this action?")

    _flag_contradictions(analysis, log)
    return analysis, log