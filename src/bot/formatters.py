"""Human-readable Telegram message formatters for Trello events."""

from src.trello.models import EventType, TrelloEvent

_EMOJI: dict[EventType, str] = {
    EventType.NEW_TASK: "🆕",
    EventType.TASK_DELETED: "🗑️",
    EventType.TASK_MOVED: "🔀",
    EventType.TASK_UPDATED: "✏️",
}

_LABEL: dict[EventType, str] = {
    EventType.NEW_TASK: "New Task Created",
    EventType.TASK_DELETED: "Task Deleted",
    EventType.TASK_MOVED: "Task Moved",
    EventType.TASK_UPDATED: "Task Updated",
}


def format_event(event: TrelloEvent) -> str:
    """Render a ``TrelloEvent`` as a nicely formatted HTML message."""
    emoji = _EMOJI[event.event_type]
    label = _LABEL[event.event_type]

    actor_name = (
        f"{event.actor.full_name} (@{event.actor.username})"
        if event.actor
        else "Unknown"
    )

    assignees_str = (
        ", ".join(
            f"{m.full_name} (@{m.username})" for m in event.assignees
        )
        if event.assignees
        else "Unassigned"
    )

    time_str = event.occurred_at.strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = [
        f"{emoji} <b>{label}</b>",
        "",
        f"🃏 <b>Card:</b> {event.card_name}",
    ]

    if event.event_type == EventType.TASK_MOVED:
        lines.append(f"🔀 <b>From:</b> {event.from_list or '?'} → <b>To:</b> {event.to_list or '?'}")
    elif event.event_type == EventType.NEW_TASK and event.to_list:
        lines.append(f"📁 <b>List:</b> {event.to_list}")
    elif event.event_type == EventType.TASK_UPDATED and event.card_desc:
        lines.append(f"📝 <b>Changed fields:</b> {event.card_desc}")

    lines += [
        "",
        f"👤 <b>By:</b> {actor_name}",
        f"👥 <b>Assigned to:</b> {assignees_str}",
        f"🕐 <b>Time:</b> {time_str}",
    ]

    if event.card_url:
        lines.append(f'🔗 <a href="{event.card_url}">Open Card</a>')
    if event.board_url:
        lines.append(f'📋 <a href="{event.board_url}">Open Board</a>')

    return "\n".join(lines)
