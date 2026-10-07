"""Person validator: ambiguous, unknown and role owners must not be accepted as people."""
from src.tools.person_validator import validate_person


def test_ambiguous_first_name_is_not_guessed():
    result = validate_person("Laura")
    assert result["status"] == "ambiguous"
    assert {m["name"] for m in result["matches"]} == {"Laura Meyer", "Laura Schmidt"}


def test_full_name_is_found():
    assert validate_person("Laura Meyer")["status"] == "found"


def test_unique_first_name_is_found():
    result = validate_person("Tom")
    assert result["status"] == "found"
    assert result["matches"][0]["name"] == "Tom Becker"


def test_role_is_not_a_person():
    assert validate_person("project managers")["status"] == "role"


def test_unknown_person_is_flagged():
    assert validate_person("Bob")["status"] == "unknown"


def test_empty_name():
    assert validate_person("")["status"] == "none"