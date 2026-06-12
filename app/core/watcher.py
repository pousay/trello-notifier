import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict

from app.core.source import EventSource
from app.bot.client import TelegramClient

logger = logging.getLogger(__name__)


class EventWatcher:
    def __init__(
        self,
        source: EventSource,
        bot: TelegramClient,
        interval: int,
        board_url: str,
    ) -> None:
        self.source = source
        self.bot = bot
        self.interval = interval
        self.board_url = board_url

        self.last_seen_id: Optional[str] = None

    # -----------------------------
    # Helpers
    # -----------------------------
    def _is_recent(self, action: Dict) -> bool:
        """
        Only allow events from last POLL_INTERVAL window.
        """
        try:
            action_time = datetime.fromisoformat(action["date"].replace("Z", "+00:00"))

            now = datetime.now(timezone.utc)
            delta = now - action_time

            return delta <= timedelta(seconds=self.interval)

        except Exception:
            return False

    def _extract(self, action: dict) -> dict:
        data = action.get("data", {})

        # action type (createCard, updateCard, commentCard, etc.)
        action_type = action.get("type", "unknown")

        actor = action.get("memberCreator", {}).get("fullName", "Unknown")

        card = data.get("card", {})
        card_name = card.get("name", "Unknown Task")

        list_before = data.get("listBefore", {}).get("name")
        list_after = data.get("listAfter", {}).get("name")

        # assigned users (if available)
        id_members = data.get("idMembers", [])

        return {
            "type": action_type,
            "actor": actor,
            "card": card_name,
            "list_before": list_before,
            "list_after": list_after,
            "members": id_members,
            "date": action.get("date", ""),
        }

    def _format(self, e: dict) -> str:
        action_type = e["type"]

        # map Trello actions → human meaning
        type_map = {
            "createCard": "🆕 Created task",
            "updateCard": "✏️ Updated task",
            "deleteCard": "🗑 Deleted task",
            "moveCard": "📦 Moved task",
            "commentCard": "💬 Commented",
            "addMemberToCard": "👤 Assigned user",
        }

        action_label = type_map.get(action_type, f"🔔 {action_type}")

        # move detection
        move = ""
        if e["list_before"] and e["list_after"]:
            move = f"📦 {e['list_before']} → {e['list_after']}"

        # involved people
        members = ", ".join(e["members"]) if e["members"] else "—"

        return (
            f"{action_label}\n\n"
            f"👤 Actor: {e['actor']}\n"
            f"👥 Involved: {members}\n"
            f"📝 Task: {e['card']}\n"
            f"{move}\n"
            f"🕒 {e['date']}\n\n"
            f"🔗 {self.board_url}"
        )

    # -----------------------------
    # Main loop
    # -----------------------------

    async def run(self, set_last_seen_callback=None) -> None:
        logger.info("Watcher started (future-only mode): %s", self.source.name())

        while True:
            try:
                actions = self.source.fetch_raw_actions(limit=20)

                if not actions:
                    await asyncio.sleep(self.interval)
                    continue

                # -----------------------------------
                # FIRST RUN: establish baseline ONLY
                # -----------------------------------
                if self.last_seen_id is None:
                    self.last_seen_id = actions[0]["id"]

                    if set_last_seen_callback:
                        set_last_seen_callback(self.last_seen_id)

                    logger.info("Initialized cursor, skipping historical events")
                    await asyncio.sleep(self.interval)
                    continue

                # -----------------------------------
                # PROCESS ONLY NEW EVENTS
                # -----------------------------------
                new_actions = []

                for action in actions:
                    if action["id"] == self.last_seen_id:
                        break
                    new_actions.append(action)

                # update cursor
                if actions:
                    self.last_seen_id = actions[0]["id"]

                    if set_last_seen_callback:
                        set_last_seen_callback(self.last_seen_id)

                # send messages
                for action in reversed(new_actions):
                    extracted = self._extract(action)
                    msg = self._format(extracted)

                    await self.bot.send(msg)
                    logger.info("Sent event %s", action["id"])

            except Exception as e:
                logger.exception("Watcher error: %s", e)

            await asyncio.sleep(self.interval)
