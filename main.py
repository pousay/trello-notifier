import asyncio
import logging

from aiogram import Dispatcher

from app.config import settings
from app.logging import setup_logging

from app.bot.client import TelegramClient
from app.bot.router import router, set_last_seen

from app.sources.trello import TrelloSource
from app.core.watcher import EventWatcher

logger = logging.getLogger(__name__)


async def main() -> None:
    # -------------------------
    # Logging
    # -------------------------
    setup_logging()
    logger.info("Starting Telegram Event Tracker...")

    # -------------------------
    # Telegram bot + dispatcher
    # -------------------------
    tg_client = TelegramClient()
    dp = Dispatcher()

    dp.include_router(router)

    # -------------------------
    # Event source
    # -------------------------
    source = TrelloSource()

    # -------------------------
    # Watcher service
    # -------------------------
    watcher = EventWatcher(
        source=source,
        bot=tg_client,
        interval=settings.POLL_INTERVAL,
    )

    # Run watcher in background (non-blocking)
    asyncio.create_task(watcher.run(set_last_seen))

    logger.info("Watcher started, polling Telegram updates...")

    # -------------------------
    # Start bot polling
    # -------------------------
    await dp.start_polling(tg_client.bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
