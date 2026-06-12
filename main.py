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
    setup_logging()

    bot = TelegramClient()
    dp = Dispatcher()
    dp.include_router(router)

    source = TrelloSource()

    board_url = f"https://trello.com/b/{settings.TRELLO_BOARD_ID}"

    watcher = EventWatcher(
        source=source,
        bot=bot,
        interval=settings.POLL_INTERVAL,
        board_url=board_url,
    )

    asyncio.create_task(watcher.run(set_last_seen))

    await dp.start_polling(bot.bot)


if __name__ == "__main__":
    asyncio.run(main())
