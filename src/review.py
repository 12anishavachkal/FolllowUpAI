"""Human review loop: the user approves, rejects, modifies or completes each item.

Nothing is saved here. The caller saves only APPROVED items after a final confirmation.
`ask` and `show` can be replaced (for example in tests) so no real typing is needed.
"""

from datetime import date
from typing import Callable

from src.models import DeadlineStatus, ItemType, MeetingItem, ReviewStatus
from src.tools.date_validator import validate_deadline
from src.tools.person_validator import TeamFileError, validate_person
from src.tools.summary import render_item

Ask = Callable[[str], str]
Show = Callable[[str], None]

MENU = ("[a] approve  [r] reject  [m] modify  "
        "[c] complete owner/deadline  [s] skip  [q] finish review")


def _ask(ask: Ask, prompt: str) -> str:
    """Read one answer. End of input counts as 'q' so nothing is approved by accident."""
    try:
        return ask(prompt).strip()
    except EOFError:
        return "q"


def ask_yes_no(ask: Ask, prompt: str, default: bool = False) -> bool:
    """Ask a yes/no question. Enter gives the default."""
    answer = _ask(ask, prompt).lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def _edit_text(item: MeetingItem, field: str, label: str, ask: Ask) -> None:
    text = _ask(ask, f"  {label} [{getattr(item, field)}] (Enter = keep): ")
    if text:
        setattr(item, field, text)


def _edit_owner(item: MeetingItem, ask: Ask, show: Show) -> None:
    """Let the user set the owner. The name is checked against the team list."""
    while True:
        text = _ask(ask, f"  Owner [{item.owner or 'none'}] (Enter = keep, - = clear): ")
        if not text:
            return
        if text == "-":
            item.owner = None
            return
        try:
            result = validate_person(text)
        except TeamFileError as exc:
            show(f"  Team list unavailable ({exc}). Owner was not validated.")
            item.owner = text
            return
        status = result["status"]
        if status == "found":
            item.owner = result["matches"][0]["name"]
            show(f"  Owner set to {item.owner}.")
            return
        if status == "ambiguous":
            names = ", ".join(m["name"] for m in result["matches"])
            show(f"  Several people match: {names}. Please type the full name.")
            continue
        show(f"  {result['note']}")
        if ask_yes_no(ask, f"  Use '{text}' anyway? [y/N]: "):
            item.owner = text
            return


def _edit_deadline(item: MeetingItem, meeting_date: str, ask: Ask, show: Show) -> None:
    """Let the user set an exact deadline. Vague wording is refused."""
    while True:
        text = _ask(ask, f"  Deadline [{item.deadline_raw or 'none'}] "
                         "(Enter = keep, - = clear, or an exact date such as 2026-11-15): ")
        if not text:
            return
        if text == "-":
            item.deadline_raw = None
            item.deadline_date = None
            item.deadline_status = DeadlineStatus.NONE
            return
        check = validate_deadline(text, meeting_date)
        if check["status"] == "resolved":
            item.deadline_raw = text
            item.deadline_date = date.fromisoformat(check["date"])
            item.deadline_status = DeadlineStatus.RESOLVED
            show(f"  Deadline set to {check['date']}.")
            return
        show(f"  {check['note']} Please enter an exact date such as 2026-11-15.")


def _snapshot(item: MeetingItem) -> tuple:
    return (item.title, item.description, item.owner, item.deadline_raw, item.deadline_date)


def _after_edit(item: MeetingItem, before: tuple, ask: Ask) -> None:
    """Record the edit. The human decides whether the open question is now resolved."""
    if _snapshot(item) == before:
        return
    item.was_modified = True
    if item.needs_clarification and ask_yes_no(
            ask, "  Mark the open question as resolved? [y/N]: "):
        item.needs_clarification = False
        item.clarification_question = None


def _modify(item: MeetingItem, meeting_date: str, ask: Ask, show: Show) -> None:
    before = _snapshot(item)
    _edit_text(item, "title", "Title", ask)
    _edit_text(item, "description", "Description", ask)
    _edit_owner(item, ask, show)
    _edit_deadline(item, meeting_date, ask, show)
    _after_edit(item, before, ask)


def _complete(item: MeetingItem, meeting_date: str, ask: Ask, show: Show) -> None:
    if item.owner and item.deadline_status == DeadlineStatus.RESOLVED:
        show("  Owner and deadline are already set. Use [m] to change them.")
        return
    before = _snapshot(item)
    if not item.owner:
        _edit_owner(item, ask, show)
    if item.deadline_status != DeadlineStatus.RESOLVED:
        _edit_deadline(item, meeting_date, ask, show)
    _after_edit(item, before, ask)


def _counts(items: list[MeetingItem]) -> dict:
    return {
        "approved": sum(1 for i in items if i.status == ReviewStatus.APPROVED),
        "rejected": sum(1 for i in items if i.status == ReviewStatus.REJECTED),
        "pending": sum(1 for i in items if i.status == ReviewStatus.PENDING),
    }


def review_items(items: list[MeetingItem], meeting_date: str,
                 ask: Ask = input, show: Show = print) -> dict:
    """Walk through the items one by one. Items are changed in place.

    Returns counts of approved, rejected and pending items.
    """
    reviewable = [i for i in items if i.type != ItemType.BACKGROUND]
    skipped = len(items) - len(reviewable)
    note = f" ({skipped} background item(s) not reviewed)" if skipped else ""
    show(f"\nREVIEW: {len(reviewable)} items to review{note}.")
    show("Nothing is saved until you confirm at the end.")

    for number, item in enumerate(reviewable, start=1):
        while True:
            show(f"\n--- Item {number} of {len(reviewable)} ({item.type.value}) ---")
            show(render_item(item))
            choice = _ask(ask, f"{MENU}\n> ").lower()

            if choice == "a":
                if item.needs_clarification and not ask_yes_no(
                        ask, "  This item still has an open question. Approve anyway? [y/N]: "):
                    continue
                item.status = ReviewStatus.APPROVED
                show("  -> approved")
                break
            if choice == "r":
                item.status = ReviewStatus.REJECTED
                show("  -> rejected")
                break
            if choice == "m":
                _modify(item, meeting_date, ask, show)
                continue
            if choice == "c":
                _complete(item, meeting_date, ask, show)
                continue
            if choice == "s":
                show("  -> skipped (stays pending and will not be saved)")
                break
            if choice == "q":
                return _counts(reviewable)
            show("  Please type a, r, m, c, s or q.")

    return _counts(reviewable)