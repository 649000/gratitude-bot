
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_or_create_user,
    get_random_entry,
    get_session,
)


async def surprise_command(
    update: Update, _context: CallbackContext
) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=user.id)
        entry = await get_random_entry(session, db_user.id)
        await session.commit()

    if entry is None:
        await update.message.reply_text(
            "Your jar is empty! Write your first entry with /grateful 🫙"
        )
        return

    star_label = "⭐ Unstar" if entry.starred else "⭐ Star"
    keyboard = [
        [
            InlineKeyboardButton(star_label, callback_data=f"star:{entry.id}"),
            InlineKeyboardButton("🗑 Delete", callback_data=f"del:{entry.id}"),
        ]
    ]
    await update.message.reply_text(
        f"🎁 Here's a surprise from your jar:\n\n"
        f"\"{entry.content}\"\n\n"
        f"_{entry.created_at.strftime('%Y-%m-%d %H:%M')}_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
