from telegram import Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    delete_entry,
    get_entry_by_id,
    get_session,
)


async def star_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    entry_id = query.data.split(":", 1)[1]

    async with get_session() as session:
        entry = await get_entry_by_id(session, entry_id)
        if entry:
            entry.starred = not entry.starred
            await session.commit()

            star_label = "⭐ Unstar" if entry.starred else "⭐ Star"
            await query.answer(f"{'⭐ Starred!' if entry.starred else 'Unstarred'}")

            keyboard = query.message.reply_markup.inline_keyboard
            if keyboard:
                keyboard[0][0].callback_data = f"star:{entry_id}"
                keyboard[0][0].text = star_label
        else:
            await query.answer("Entry not found")


async def delete_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    entry_id = query.data.split(":", 1)[1]

    async with get_session() as session:
        success = await delete_entry(session, entry_id)
        if success:
            await session.commit()

    if success:
        await query.edit_message_text("🗑 Deleted")
    else:
        await query.answer("Entry not found")
