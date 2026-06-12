"""Command handlers: /status, /all, /card."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.trello.client import TrelloClient
from src.trello.models import TrelloList

logger = logging.getLogger(__name__)


def build_commands_router(trello_client: TrelloClient) -> Router:
    """Return a router with all command handlers bound to ``trello_client``."""
    router = Router(name="commands")

    @router.message(Command("status"))
    async def cmd_status(message: Message) -> None:
        """Check bot and Trello API health."""
        logger.info("/status requested by user %s", message.from_user.id if message.from_user else "?")
        try:
            board = await trello_client.get_board()
            name = board.get("name", "Unknown")
            await message.answer(
                f"✅ <b>Bot is running.</b>\n"
                f"📋 Connected to board: <b>{name}</b>"
            )
        except Exception as exc:
            logger.exception("Trello health-check failed")
            await message.answer(f"⚠️ Bot is running but Trello check failed:\n<code>{exc}</code>")

    @router.message(Command("all"))
    async def cmd_all(message: Message) -> None:
        """List every open card grouped by list."""
        logger.info("/all requested by user %s", message.from_user.id if message.from_user else "?")
        try:
            raw_lists = await trello_client.get_lists()
            raw_cards = await trello_client.get_cards()

            lists: dict[str, str] = {lst["id"]: lst["name"] for lst in raw_lists}
            grouped: dict[str, list[str]] = {name: [] for name in lists.values()}

            for card in raw_cards:
                list_name = lists.get(card["idList"], "Unknown")
                grouped.setdefault(list_name, []).append(card["name"])

            if not any(grouped.values()):
                await message.answer("📭 No open cards found on this board.")
                return

            lines = ["📋 <b>All Cards on Board</b>\n"]
            for list_name, cards in grouped.items():
                if cards:
                    lines.append(f"\n<b>📁 {list_name}</b>")
                    for card_name in cards:
                        lines.append(f"  • {card_name}")

            await message.answer("\n".join(lines))
        except Exception as exc:
            logger.exception("Failed to fetch all cards")
            await message.answer(f"❌ Could not fetch cards:\n<code>{exc}</code>")

    @router.message(Command("card"))
    async def cmd_card(message: Message) -> None:
        """Show details of cards whose name contains the given query."""
        logger.info("/card requested by user %s", message.from_user.id if message.from_user else "?")
        if not message.text:
            await message.answer("Usage: /card <card name>")
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await message.answer("Usage: /card <card name>")
            return

        query = parts[1].strip().lower()

        try:
            raw_lists = await trello_client.get_lists()
            raw_cards = await trello_client.get_cards()
            lists: dict[str, str] = {lst["id"]: lst["name"] for lst in raw_lists}

            matches = [c for c in raw_cards if query in c["name"].lower()]

            if not matches:
                await message.answer(f'🔍 No cards matching "<b>{query}</b>" found.')
                return

            lines = [f'🔍 <b>Cards matching "{query}"</b>\n']
            for card in matches:
                list_name = lists.get(card["idList"], "Unknown")
                members = card.get("members", [])
                assigned = (
                    ", ".join(m.get("fullName", m.get("username", "?")) for m in members)
                    or "Unassigned"
                )
                desc = card.get("desc", "").strip()
                due = card.get("due", None)

                lines.append(f"\n<b>🃏 {card['name']}</b>")
                lines.append(f"  📁 List: {list_name}")
                lines.append(f"  👤 Assigned: {assigned}")
                if due:
                    lines.append(f"  ⏰ Due: {due[:10]}")
                if desc:
                    lines.append(f"  📝 {desc[:120]}{'...' if len(desc) > 120 else ''}")
                lines.append(f'  🔗 <a href="{card.get("shortUrl", "")}">Open card</a>')

            await message.answer("\n".join(lines), disable_web_page_preview=True)
        except Exception as exc:
            logger.exception("Failed to fetch card details")
            await message.answer(f"❌ Could not fetch card:\n<code>{exc}</code>")

    return router
