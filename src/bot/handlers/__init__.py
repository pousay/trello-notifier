"""Handler registration."""

from aiogram import Dispatcher

from src.trello.client import TrelloClient
from src.bot.handlers.commands import build_commands_router
from src.bot.handlers.callbacks import build_callbacks_router


def register_handlers(dp: Dispatcher, trello_client: TrelloClient) -> None:
    """Attach all routers to the dispatcher."""
    dp.include_router(build_commands_router(trello_client))
    dp.include_router(build_callbacks_router())
