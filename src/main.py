"""Command-line entry point.  Run: python -m src.main samples/example_pdf.md"""

import argparse
import sys
from datetime import date

from src.analyze import AnalysisError, analyze_notes
from src.llm import LLMConfigError
from src.tools.note_reader import NoteReadError, read_meeting_notes
from src.tools.summary import render_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Meeting follow-up agent (draft analysis).")
    parser.add_argument("notes_file", help="Path to a .txt or .md notes file")
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Meeting date YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", help="Also print the structured JSON")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())