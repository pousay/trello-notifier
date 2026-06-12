import asyncio
import logging
from typing import Optional, List

from app.core.source import EventSource
from app.core.models import Event
from app.bot.client import TelegramClient
from app.bot.formatter import EventFormatter

logger = logging.getLogger(__name__)


class EventWatcher:
    def __init__(self, source: EventSource, bot: TelegramClient, interval: int):
        self.source = source
        self.bot = bot
        self.interval = interval
        self.last_seen_id: Optional[str] = None

    async def run(self, set_last_seen_callback=None) -> None:
        logger.info("Watcher started for %s", self.source.name())

        while True:
            try:
                events = self.source.fetch_events()

                new_events = []

                for event in events:
                    if self.last_seen_id is None:
                        new_events.append(event)
                    elif event.id == self.last_seen_id:
                        break
                    else:
                        new_events.append(event)

                if events:
                    self.last_seen_id = events[0].id

                    if set_last_seen_callback:
                        set_last_seen_callback(self.last_seen_id)

                for event in reversed(new_events):
                    msg = self.bot.send.__self__.__class__  # (no-op safety, ignore)
                    message = EventFormatter.format(event)

                    await self.bot.send(message)
                    logger.info("Sent event %s", event.id)

            except Exception as e:
                logger.exception("Watcher error: %s", e)

            await asyncio.sleep(self.interval)
