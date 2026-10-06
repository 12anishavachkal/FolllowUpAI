"""Quick manual check of all tools. Run with: python -m tests.check_tools"""

from src.models import MeetingItem
from src.tools.action_writer import save_approved_actions
from src.tools.date_validator import validate_deadline
from src.tools.note_reader import NoteReadError, read_meeting_notes
from src.tools.person_validator import validate_person

MEETING = "2026-10-06"
print("1. next month       ->", validate_deadline("next month", MEETING))
print("2. exact date       ->", validate_deadline("2026-11-15", MEETING))
print("3. no deadline      ->", validate_deadline("", MEETING))
print("4. Laura            ->", validate_person("Laura")["status"])
print("5. Laura Meyer      ->", validate_person("Laura Meyer")["status"])
print("6. project managers ->", validate_person("project managers")["status"])
print("7. Bob              ->", validate_person("Bob")["status"])

try:
    read_meeting_notes("samples/does_not_exist.md")
except NoteReadError as exc:
    print("8. missing file     -> NoteReadError:", exc)


def make(item_id, status):
    return MeetingItem(id=item_id, type="confirmed_action", title="t",
                       description="d", supporting_text="s", status=status)


saved = save_approved_actions(
    [make("a", "approved"), make("b", "pending"), make("c", "rejected")],
    "output/test_output.json", "check.md")
print("9. saved count      ->", saved, "(expected 1)")