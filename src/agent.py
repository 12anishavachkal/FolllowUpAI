"""The Gemini-powered agent: reads notes, calls validator tools, returns a MeetingAnalysis."""

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from src.config import load_settings, resolve_path
from src.llm import get_model
from src.models import MeetingAnalysis
from src.tools.date_validator import validate_deadline
from src.tools.person_validator import TeamFileError, validate_person


@dataclass
class AgentDeps:
    """Values the tools need but the model should not have to repeat."""

    meeting_date: str  # YYYY-MM-DD


def build_agent() -> Agent[AgentDeps, MeetingAnalysis]:
    """Create the agent with its rules (from config) and its two tools."""
    prompt_path = resolve_path(load_settings()["paths"]["system_prompt"])
    instructions = prompt_path.read_text(encoding="utf-8")

    agent = Agent(
        get_model(),
        deps_type=AgentDeps,
        output_type=MeetingAnalysis,
        instructions=instructions,
        retries=2,  # lets the model fix an invalid answer before giving up
    )

    @agent.tool
    def check_deadline(ctx: RunContext[AgentDeps], raw_text: str) -> dict:
        """Check a deadline wording from the notes (for example 'next month' or '2026-11-15').

        Returns status resolved, needs_clarification, none or error, and an exact date
        only when the wording is certain. Never convert vague wording yourself.
        """
        return validate_deadline(raw_text, ctx.deps.meeting_date)

    @agent.tool_plain
    def check_person(name_or_role: str) -> dict:
        """Check a person's name or a role against the fictional team list.

        Returns status found, ambiguous, unknown, role, none or error.
        Call this for every owner before you set one.
        """
        try:
            return validate_person(name_or_role)
        except TeamFileError as exc:
            return {"status": "error", "query": name_or_role, "matches": [],
                    "note": f"Team list unavailable ({exc}). Do not assign an owner."}

    return agent