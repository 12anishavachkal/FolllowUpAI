"""Tool: turn a MeetingAnalysis into a readable plain-text follow-up summary."""

from src.models import DeadlineStatus, ItemType, MeetingAnalysis, MeetingItem

SECTIONS = [
    (ItemType.CONFIRMED_DECISION, "CONFIRMED DECISIONS"),
    (ItemType.PROPOSED_DECISION, "PROPOSED DECISIONS (not yet agreed)"),
    (ItemType.CONFIRMED_ACTION, "CONFIRMED ACTIONS"),
    (ItemType.POSSIBLE_ACTION, "POSSIBLE ACTIONS (not agreed)"),
    (ItemType.OPEN_QUESTION, "OPEN QUESTIONS"),
    (ItemType.RISK, "RISKS AND CONCERNS"),
    (ItemType.BACKGROUND, "BACKGROUND"),
    (ItemType.UNCLEAR, "UNCLEAR"),
]
ACTION_TYPES = (ItemType.CONFIRMED_ACTION, ItemType.POSSIBLE_ACTION)


def _deadline_text(item: MeetingItem) -> str:
    if item.deadline_status == DeadlineStatus.RESOLVED and item.deadline_date:
        return f"{item.deadline_date.isoformat()} (notes say '{item.deadline_raw}')"
    if item.deadline_status == DeadlineStatus.NEEDS_CLARIFICATION:
        return f"UNCLEAR (notes say '{item.deadline_raw}')"
    return "none mentioned"


def render_item(item: MeetingItem) -> str:
    """Format one item as indented plain text."""
    lines = [f"  [{item.id}] {item.title}", f"      {item.description}"]
    is_action = item.type in ACTION_TYPES
    if is_action or item.owner:
        lines.append(f"      Owner: {item.owner or 'NOT ASSIGNED'}")
    if is_action or item.deadline_raw:
        lines.append(f"      Deadline: {_deadline_text(item)}")
    lines.append(f'      Source: "{item.supporting_text}"')
    if item.needs_clarification:
        lines.append(f"      [!] Clarify: {item.clarification_question}")
    return "\n".join(lines)


def render_summary(analysis: MeetingAnalysis, corrections: list[str] | None = None) -> str:
    """Build the full readable follow-up summary."""
    out = ["MEETING FOLLOW-UP (DRAFT - nothing has been saved)", "=" * 60]
    if analysis.meeting_title:
        out.append(f"Meeting: {analysis.meeting_title}")
    out += ["", "SUMMARY", analysis.summary]
    if analysis.topics:
        out.append("Topics: " + "; ".join(analysis.topics))

    for item_type, heading in SECTIONS:
        group = [i for i in analysis.items if i.type == item_type]
        if group:
            out += ["", f"{heading} ({len(group)})"]
            out += [render_item(i) for i in group]

    if analysis.contradictions:
        out += ["", "CONTRADICTIONS FOUND"]
        out += [f"  - {c}" for c in analysis.contradictions]

    flagged = sum(1 for i in analysis.items if i.needs_clarification)
    out += ["", f"{flagged} of {len(analysis.items)} items need clarification."]

    if corrections:
        out += ["", "AUTOMATIC CHECKS (corrections made after the model answered)"]
        out += [f"  - {c}" for c in corrections]
    return "\n".join(out)