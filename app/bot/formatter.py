from app.core.models import Event


class EventFormatter:
    @staticmethod
    def format(event: Event) -> str:
        return (
            f"📌 <b>{event.source} Event</b>\n\n"
            f"👤 {event.actor or 'Unknown'}\n"
            f"🔔 {event.title}\n"
            f"🗂 {event.description or '-'}\n\n"
            f"🕒 {event.created_at.isoformat()}"
        )
