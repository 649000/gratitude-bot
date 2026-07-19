
from telegram import Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    create_entry,
    get_or_create_user,
    get_random_prompt,
    get_session,
)


async def grateful_command(
    update: Update, context: CallbackContext
) -> None:
    user = update.effective_user
    async with get_session() as session:
        _db_user = await get_or_create_user(session, telegram_id=user.id)
        prompt = await get_random_prompt(session)
        context.chat_data["waiting_entry"] = True
        await session.commit()

    await update.message.reply_text(prompt)


async def save_entry_handler(
    update: Update, context: CallbackContext
) -> None:
    if not context.chat_data.get("waiting_entry"):
        return

    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=user.id)
        await create_entry(session, db_user.id, update.message.text)
        await session.commit()

    context.chat_data["waiting_entry"] = False
    await update.message.reply_text("✨ Saved!")
