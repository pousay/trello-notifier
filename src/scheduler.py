"""Async polling scheduler that bridges the Trello tracker and Telegram bot."""

import asyncio
import logging

from aiogram import Bot

from src.trello.base import AbstractEventTracker
from src.trello.models import TrelloEvent, EventType
from src.bot.formatters import format_event
from src.bot.keyboards import done_keyboard

logger = logging.getLogger(__name__)


class PollingScheduler:
    """Polls the Trello tracker at a fixed interval and dispatches messages."""

    def __init__(
        self,
        tracker: AbstractEventTracker,
        bot: Bot,
        chat_id: int,
        interval: int = 30,
    ) -> None:
        self._tracker = tracker
        self._bot = bot
        self._chat_id = chat_id
        self._interval = interval

    async def run(self) -> None:
        """Run the polling loop indefinitely."""
        logger.info("Polling scheduler started (interval=%ss)", self._interval)

        # Initialise snapshot — establishes baseline, fires no notifications
        await self._tracker.initialise()
        logger.info("Tracker initialised — watching for new events only.")

        while True:
            await asyncio.sleep(self._interval)
            try:
                events: list[TrelloEvent] = await self._tracker.poll()
                for event in events:
                    await self._dispatch(event)
            except Exception:
                logger.exception("Error during poll cycle")

    async def _dispatch(self, event: TrelloEvent) -> None:
        """Send a single event notification to Telegram."""
        text = format_event(event)
        markup = done_keyboard()
        try:
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup,
                disable_web_page_preview=True,
            )
            logger.info(
                "Dispatched event type=%s card=%s",
                event.event_type.value,
                event.card_name,
            )
        except Exception:
            logger.exception("Failed to send event notification for card %s", event.card_name)
