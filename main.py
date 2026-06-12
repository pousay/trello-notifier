#!/usr/bin/env python3
"""Entry point for the Trello Telegram Bot."""

import asyncio
import logging

from src.config import get_settings
from src.bot.app import create_bot
from src.scheduler import PollingScheduler
from src.trello.tracker import TrelloEventTracker
from src.trello.client import TrelloClient

logger = logging.getLogger(__name__)


def setup_logging(level: str) -> None:
    """Configure root logger with both console and file handlers."""
    import os
    os.makedirs("logs", exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


async def main() -> None:
    """Bootstrap and run the bot + polling scheduler concurrently."""
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting Trello Telegram Bot...")
    logger.info(
        "Board: %s | Poll interval: %ss",
        settings.trello_board_id,
        settings.poll_interval_seconds,
    )

    trello_client = TrelloClient(
        api_key=settings.trello_api_key,
        api_token=settings.trello_api_token,
        board_id=settings.trello_board_id,
    )

    tracker = TrelloEventTracker(client=trello_client)

    bot, dp = create_bot(settings=settings, trello_client=trello_client)

    scheduler = PollingScheduler(
        tracker=tracker,
        bot=bot,
        chat_id=settings.telegram_chat_id,
        interval=settings.poll_interval_seconds,
    )

    async with bot.session:
        await asyncio.gather(
            dp.start_polling(bot),
            scheduler.run(),
        )


if __name__ == "__main__":
    asyncio.run(main())
