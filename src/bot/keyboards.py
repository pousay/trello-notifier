"""Reusable inline keyboard builders."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.handlers.callbacks import DONE_CALLBACK


def done_keyboard() -> InlineKeyboardMarkup:
    """Return an inline keyboard with a single ✅ Done button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Done", callback_data=DONE_CALLBACK)]
        ]
    )
