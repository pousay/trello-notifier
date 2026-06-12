"""Bot and dispatcher factory."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import Settings
from src.trello.client import TrelloClient
from src.bot.handlers import register_handlers

logger = logging.getLogger(__name__)


def create_bot(settings: Settings, trello_client: TrelloClient) -> tuple[Bot, Dispatcher]:
    """Instantiate and configure the bot and dispatcher."""
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    register_handlers(dp, trello_client=trello_client)
    logger.info("Bot and dispatcher ready.")
    return bot, dp
