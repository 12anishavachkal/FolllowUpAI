"""File-processing failures must end in clear messages, not crashes."""
import sys

import pytest

from src.analyze import AnalysisError, analyze_notes
from src.tools.note_reader import NoteReadError, read_meeting_notes


def test_missing_file(tmp_path):
    with pytest.raises(NoteReadError, match="File not found"):
        read_meeting_notes(str(tmp_path / "nope.md"))


def test_empty_file(tmp_path):
    f = tmp_path / "empty.md"
    f.write_text("", encoding="utf-8")
    with pytest.raises(NoteReadError, match="empty"):
        read_meeting_notes(str(f))


def test_unsupported_type(tmp_path):
    f = tmp_path / "notes.docx"
    f.write_text("not a real Word file", encoding="utf-8")
    with pytest.raises(NoteReadError, match="Unsupported file type"):
        read_meeting_notes(str(f))


def test_file_too_large(tmp_path):
    f = tmp_path / "big.txt"
    f.write_text("x" * 100_001, encoding="utf-8")
    with pytest.raises(NoteReadError, match="too large"):
        read_meeting_notes(str(f))


def test_file_that_is_not_utf8(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_bytes(b"\x80\x81\x82")
    with pytest.raises(NoteReadError, match="UTF-8"):
        read_meeting_notes(str(f))


def test_valid_file_is_read(tmp_path):
    f = tmp_path / "ok.md"
    f.write_text("Tom will write the report.", encoding="utf-8")
    assert "Tom will" in read_meeting_notes(str(f))


def test_bad_meeting_date_fails_before_any_model_call():
    with pytest.raises(AnalysisError, match="must look like"):
        analyze_notes("Some notes.", "06-10-2026")


def test_command_line_reports_missing_file_with_exit_code_1(tmp_path, monkeypatch, capsys):
    from src.main import main
    monkeypatch.setattr(sys, "argv", ["main", str(tmp_path / "missing.md")])
    assert main() == 1
    assert "Cannot read notes" in capsys.readouterr().out