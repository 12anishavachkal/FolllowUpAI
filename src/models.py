"""Data models for the Meeting Follow-up Agent.

These models define the structured output of the agent. Key design rules:
  * Owners and deadlines are OPTIONAL: the agent must never invent them.
  * Every item carries the original supporting text from the notes.
  * Every item starts as PENDING; only APPROVED items may be saved.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ItemType(str, Enum):
    """What kind of statement was found in the meeting notes."""

    CONFIRMED_DECISION = "confirmed_decision"  # clearly decided by the group
    PROPOSED_DECISION = "proposed_decision"    # suggested, "should probably", not agreed
    CONFIRMED_ACTION = "confirmed_action"      # clearly agreed task
    POSSIBLE_ACTION = "possible_action"        # maybe a task, not agreed
    OPEN_QUESTION = "open_question"            # still to be decided or answered
    RISK = "risk"                              # risk or concern raised
    BACKGROUND = "background"                  # context only, no follow-up needed
    UNCLEAR = "unclear"                        # cannot be classified from the text


class ReviewStatus(str, Enum):
    """Human review state. Only APPROVED items are ever written to disk."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DeadlineStatus(str, Enum):
    """How trustworthy the deadline information is."""

    NONE = "none"                                  # no deadline mentioned
    RESOLVED = "resolved"                          # exact date is known
    NEEDS_CLARIFICATION = "needs_clarification"    # vague, e.g. "next month"


class MeetingItem(BaseModel):
    """One decision, action, question, risk or background statement."""

    id: str = Field(description="Short unique id such as 'item-1'.")
    type: ItemType = Field(description="Category of this item.")
    title: str = Field(description="Short title, max about 10 words.")
    description: str = Field(description="One or two sentences explaining the item.")

    owner: Optional[str] = Field(
        default=None,
        description="Person responsible. Use null unless the notes explicitly "
        "name this person as responsible. NEVER guess an owner.",
    )
    deadline_raw: Optional[str] = Field(
        default=None,
        description="The deadline wording exactly as in the notes, e.g. 'next month'.",
    )
    deadline_date: Optional[date] = Field(
        default=None,
        description="Exact date (YYYY-MM-DD) ONLY if the notes make it certain.",
    )
    deadline_status: DeadlineStatus = Field(default=DeadlineStatus.NONE)

    supporting_text: str = Field(
        min_length=1,
        description="Exact sentence(s) from the notes that support this item.",
    )
    needs_clarification: bool = Field(
        default=False,
        description="True if owner, date, or meaning is uncertain.",
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="Question to ask the user when needs_clarification is true.",
    )

    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    was_modified: bool = Field(
        default=False, description="True if the human edited this item during review."
    )

    @model_validator(mode="after")
    def check_consistency(self) -> "MeetingItem":
        if self.needs_clarification and not self.clarification_question:
            raise ValueError(
                "clarification_question is required when needs_clarification is true"
            )
        if self.deadline_status == DeadlineStatus.RESOLVED and self.deadline_date is None:
            raise ValueError("deadline_date is required when deadline_status is resolved")
        if self.deadline_status != DeadlineStatus.RESOLVED and self.deadline_date is not None:
            raise ValueError("deadline_date must be empty unless deadline_status is resolved")
        return self


class MeetingAnalysis(BaseModel):
    """Full draft follow-up package produced by the agent."""

    meeting_title: Optional[str] = Field(default=None)
    topics: list[str] = Field(default_factory=list, description="Main topics discussed.")
    summary: str = Field(description="Short readable summary of the meeting.")
    items: list[MeetingItem] = Field(default_factory=list)
    contradictions: list[str] = Field(
        default_factory=list,
        description="Statements in the notes that contradict each other.",
    )

    def approved_items(self) -> list[MeetingItem]:
        """Return only items the human has approved (the only ones we may save)."""
        return [i for i in self.items if i.status == ReviewStatus.APPROVED]