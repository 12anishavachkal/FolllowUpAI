"""Retry logic: busy-service errors are retried, other errors fail immediately."""
import pytest

from src import analyze
from src.analyze import AnalysisError, _run_with_retry


class FakeApiError(Exception):
    def __init__(self, status_code):
        super().__init__(f"status_code: {status_code}")
        self.status_code = status_code


class FakeAgent:
    """Fails the first `failures` calls, then succeeds."""

    def __init__(self, failures, status_code=503):
        self.failures = failures
        self.status_code = status_code
        self.calls = 0

    def run_sync(self, prompt, deps=None):
        self.calls += 1
        if self.calls <= self.failures:
            raise FakeApiError(self.status_code)
        return "OK"


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    monkeypatch.setattr(analyze.time, "sleep", lambda seconds: None)


def test_busy_service_is_retried_then_succeeds():
    agent = FakeAgent(failures=2)
    assert _run_with_retry(agent, "p", deps=None) == "OK"
    assert agent.calls == 3


def test_busy_service_gives_clear_message_after_all_attempts():
    agent = FakeAgent(failures=99)
    with pytest.raises(AnalysisError, match="busy or unavailable"):
        _run_with_retry(agent, "p", deps=None)
    assert agent.calls == analyze.MAX_ATTEMPTS


def test_wrong_model_name_is_not_retried():
    agent = FakeAgent(failures=99, status_code=404)
    with pytest.raises(AnalysisError, match="model call failed"):
        _run_with_retry(agent, "p", deps=None)
    assert agent.calls == 1