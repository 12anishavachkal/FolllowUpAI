"""Tool: read meeting notes from a text or Markdown file, failing with clear messages."""

from pathlib import Path

from src.config import load_settings


class NoteReadError(Exception):
    """Raised when the meeting notes cannot be read safely."""


def read_meeting_notes(file_path: str) -> str:
    """Return the text of a .txt or .md notes file, or raise NoteReadError."""
    settings = load_settings()["notes"]
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise NoteReadError(f"File not found: {file_path}")
    if path.suffix.lower() not in settings["allowed_extensions"]:
        raise NoteReadError(
            f"Unsupported file type '{path.suffix}'. "
            f"Allowed: {', '.join(settings['allowed_extensions'])}"
        )
    if path.stat().st_size > settings["max_size_bytes"]:
        raise NoteReadError(
            f"File is too large (limit {settings['max_size_bytes']} bytes)."
        )

    try:
        # utf-8-sig also handles the hidden marker Windows Notepad can add
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise NoteReadError("File is not valid UTF-8 text.") from exc
    except OSError as exc:
        raise NoteReadError(f"Could not read file: {exc}") from exc

    if not text.strip():
        raise NoteReadError("The notes file is empty.")
    return text