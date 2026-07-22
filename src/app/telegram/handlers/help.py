from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.messages import (
    HELP_BTN_ENTRIES,
    HELP_BTN_GRATEFUL,
    HELP_BTN_SETTINGS,
    HELP_BTN_STAR,
    HELP_BTN_STATS,
    HELP_BTN_SURPRISE,
    HELP_MESSAGE,
)


async def help_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    name = user.first_name if user and user.first_name else "there"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(HELP_BTN_GRATEFUL, callback_data="nav:grateful"),
                InlineKeyboardButton(HELP_BTN_SURPRISE, callback_data="nav:surprise"),
            ],
            [
                InlineKeyboardButton(HELP_BTN_ENTRIES, callback_data="nav:entries"),
                InlineKeyboardButton(HELP_BTN_STAR, callback_data="nav:star"),
            ],
            [
                InlineKeyboardButton(HELP_BTN_STATS, callback_data="nav:stats"),
                InlineKeyboardButton(HELP_BTN_SETTINGS, callback_data="nav:settings"),
            ],
        ]
    )

    await update.effective_message.reply_text(
        HELP_MESSAGE.format(name=name),
        reply_markup=keyboard,
    )
