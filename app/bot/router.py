import logging
from collections import defaultdict

from aiogram import Router
from aiogram.types import Message

from app.sources.trello import TrelloSource
from app.config import settings

logger = logging.getLogger(__name__)

router = Router()

# single shared source instance (simple DI style)
trello_source = TrelloSource()

# shared runtime state (simple in-memory tracking)
_last_seen_id: str | None = None


def set_last_seen(event_id: str | None) -> None:
    global _last_seen_id
    _last_seen_id = event_id


# -----------------------------
# /status
# -----------------------------
@router.message(lambda m: m.text == "/status")
async def status_handler(message: Message):
    trello_ok = False
    error_msg = None

    try:
        _ = trello_source.fetch_events(limit=1)
        trello_ok = True
    except Exception as e:
        logger.exception("Trello health check failed")
        error_msg = str(e)

    text = (
        "📡 <b>Bot Status</b>\n\n"
        f"🤖 Bot: <b>ONLINE</b>\n"
        f"📊 Poll Interval: {settings.POLL_INTERVAL}s\n"
        f"🧩 Trello: {'🟢 OK' if trello_ok else '🔴 FAIL'}\n"
    )

    if _last_seen_id:
        text += f"🆔 Last Event ID: <code>{_last_seen_id}</code>\n"

    if error_msg:
        text += f"\n⚠️ Error: <code>{error_msg}</code>"

    await message.answer(text, parse_mode="HTML")


# -----------------------------
# helpers for /all
# -----------------------------
def group_by_card(events):
    grouped = defaultdict(list)

    for e in events:
        card_name = e.description or "Unknown Card"
        grouped[card_name].append(e)

    return grouped


def format_all(events):
    grouped = group_by_card(events)

    parts = ["📋 <b>Trello Board Overview</b>\n"]

    for card, items in grouped.items():
        parts.append(f"\n🗂 <b>{card}</b>")

        for e in items:
            parts.append(f"• {e.title} — {e.actor or 'Unknown'}")

    return "\n".join(parts)


# -----------------------------
# /all
# -----------------------------
@router.message(lambda m: m.text == "/all")
async def all_handler(message: Message):
    try:
        events = trello_source.fetch_events(limit=50)

        if not events:
            await message.answer("No events found.")
            return

        text = format_all(events)

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.exception("Failed /all command")
        await message.answer(f"Error fetching Trello data: {e}")
