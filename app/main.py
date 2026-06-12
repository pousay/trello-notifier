import asyncio

from app.config import settings
from app.logging import setup_logging
from app.bot.client import TelegramClient
from app.sources.trello import TrelloSource
from app.core.watcher import EventWatcher


async def main():
    setup_logging()

    source = TrelloSource()
    bot = TelegramClient()

    watcher = EventWatcher(
        source=source,
        bot=bot,
        interval=settings.POLL_INTERVAL,
    )

    await watcher.run()


if __name__ == "__main__":
    asyncio.run(main())
