"""Project-information search tool: facts come from the file, never from the model."""
import pytest

from src.tools import project_search
from src.tools.project_search import ProjectInfoError, search_project_info


def test_known_topic_is_found():
    result = search_project_info("export bug")
    assert result["status"] == "found"
    assert any("CSV" in m["fact"] for m in result["matches"])


def test_unknown_topic_returns_none_and_invents_nothing():
    result = search_project_info("quantum budget")
    assert result["status"] == "none" and result["matches"] == []


def test_empty_query_is_none():
    assert search_project_info("")["status"] == "none"


def test_missing_file_raises_clear_error(monkeypatch, tmp_path):
    monkeypatch.setattr(project_search, "resolve_path", lambda p: tmp_path / "nope.json")
    with pytest.raises(ProjectInfoError, match="Cannot load project information"):
        search_project_info("export")
