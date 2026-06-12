"""Inline keyboard callback handlers."""

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

DONE_CALLBACK = "done"


def build_callbacks_router() -> Router:
    """Return a router for inline keyboard callbacks."""
    router = Router(name="callbacks")

    @router.callback_query(lambda c: c.data == DONE_CALLBACK)
    async def handle_done(callback: CallbackQuery) -> None:
        """Delete the notification message when the user taps Done."""
        logger.info(
            "Done callback from user %s on message %s",
            callback.from_user.id if callback.from_user else "?",
            callback.message.message_id if callback.message else "?",
        )
        if callback.message:
            try:
                await callback.message.delete()
            except Exception:
                logger.warning("Could not delete message; it may already be gone.")
        await callback.answer()

    return router
