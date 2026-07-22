import logging
import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import delete_entry, get_entry_by_id, get_session, star_entry
from app.telegram.messages import (
    EMOJI_STAR,
    ENTRY_REMOVED,
    ENTRY_VANISHED,
    STARRED,
    UNSTARRED,
)

logger = logging.getLogger(__name__)


async def star_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    entry_id = uuid.UUID(query.data.split(":", 1)[1])

    async with get_session() as session:
        entry = await get_entry_by_id(session, entry_id)
        if not entry:
            await query.answer(ENTRY_VANISHED)
            return
        was_starred = entry.starred
        await star_entry(session, entry_id, starred=not was_starred)
        newly_starred = not was_starred

    old_markup = query.message.reply_markup
    if old_markup:
        new_label = f"{EMOJI_STAR} Unstar" if newly_starred else f"{EMOJI_STAR} Star"
        new_keyboard = []
        changed = False
        for row in old_markup.inline_keyboard:
            new_row = []
            for button in row:
                if button.callback_data and button.callback_data.startswith("star:"):
                    if button.text != new_label:
                        changed = True
                    new_row.append(
                        InlineKeyboardButton(new_label, callback_data=button.callback_data)
                    )
                else:
                    new_row.append(button)
            new_keyboard.append(new_row)
        if changed:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))

    await query.answer(STARRED if newly_starred else UNSTARRED)


async def delete_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    entry_id = uuid.UUID(query.data.split(":", 1)[1])

    async with get_session() as session:
        entry = await get_entry_by_id(session, entry_id)
        if not entry:
            await query.edit_message_text(ENTRY_VANISHED)
            return
        deleted = await delete_entry(session, entry_id)
        logger.info("delete_callback entry_id=%s deleted=%s", entry_id, deleted)

    if deleted:
        await query.edit_message_text(ENTRY_REMOVED)
    else:
        await query.edit_message_text(ENTRY_VANISHED)
