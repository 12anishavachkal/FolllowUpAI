"""Command-line entry point.  Run: python -m src.main samples/example_pdf.md"""

import argparse
import sys
from datetime import date
from pathlib import Path

from src.analyze import AnalysisError, analyze_notes
from src.config import load_settings, resolve_path
from src.llm import LLMConfigError
from src.models import ReviewStatus
from src.review import ask_yes_no, review_items
from src.tools.action_writer import ActionWriteError, save_approved_actions, saveable_types
from src.tools.note_reader import NoteReadError, read_meeting_notes
from src.tools.summary import render_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Meeting follow-up agent.")
    parser.add_argument("notes_file", help="Path to a .txt or .md notes file")
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Meeting date YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", help="Also print the structured JSON")
    parser.add_argument("--no-review", action="store_true",
                        help="Only print the draft; skip the review and save steps")
    args = parser.parse_args()

    try:
        notes = read_meeting_notes(args.notes_file)
    except NoteReadError as exc:
        print(f"Cannot read notes: {exc}")
        return 1

    try:
        analysis, corrections = analyze_notes(notes, args.date)
    except (LLMConfigError, AnalysisError) as exc:
        print(f"Analysis failed: {exc}")
        return 1

    print(render_summary(analysis, corrections))
    if args.json:
        print("\nSTRUCTURED JSON")
        print(analysis.model_dump_json(indent=2))

    if args.no_review:
        print("\nReview skipped (--no-review). Nothing was saved.")
        return 0

    counts = review_items(analysis.items, args.date)
    print(f"\nReview finished: {counts['approved']} approved, "
          f"{counts['rejected']} rejected, {counts['pending']} left pending.")

    allowed = saveable_types()
    to_save = [i for i in analysis.items
               if i.status == ReviewStatus.APPROVED and i.type.value in allowed]
    not_saved = counts["approved"] - len(to_save)
    if not_saved:
        print(f"{not_saved} approved item(s) are not actions and will not be saved "
              f"(saved types: {', '.join(sorted(allowed))}).")
    if not to_save:
        print("Nothing to save.")
        return 0

    overridden = [i for i in to_save if i.needs_clarification]
    if overridden:
        print("\nApproved with an open question (will be saved with your reason):")
        for i in overridden:
            print(f"  [{i.id}] {i.title}\n      Open: {i.clarification_question}"
                  f"\n      Reason: {i.approval_note}")

    
    output_path = resolve_path(load_settings()["paths"]["output_file"])
    if not ask_yes_no(input, f"Save {len(to_save)} approved item(s) to {output_path}? [Y/n]: ",
                      default=True):
        print("Not saved.")
        return 0

    try:
        saved = save_approved_actions(analysis.items, str(output_path), Path(args.notes_file).name)
    except ActionWriteError as exc:
        print(f"Could not save: {exc}")
        return 1
    print(f"Saved {saved} new approved item(s) to {output_path}.")
    if saved < len(to_save):
        print(f"{len(to_save) - saved} item(s) were already saved earlier and were skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())