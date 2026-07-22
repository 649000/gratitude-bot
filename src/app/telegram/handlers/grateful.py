import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    create_entry,
    get_or_create_user,
    get_random_prompt,
    get_session,
)
from app.telegram.messages import (
    EMOJI_DELETE,
    ENTRY_SAVED_RESPONSES,
    ENTRY_TOO_SHORT,
    FALLBACK_PROMPT,
    _escape_md,
    format_entry_date_local,
)

_MIN_ENTRY_LENGTH = 3


async def grateful_command(update: Update, context: CallbackContext) -> None:
    async with get_session() as session:
        await get_or_create_user(
            session,
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
        prompt = await get_random_prompt(session)

    text = prompt if prompt else FALLBACK_PROMPT
    await update.effective_message.reply_text(text)


async def save_entry_handler(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    content = update.effective_message.text.strip() if update.effective_message.text else ""

    if len(content) < _MIN_ENTRY_LENGTH:
        await update.effective_message.reply_text(ENTRY_TOO_SHORT)
        return

    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        entry = await create_entry(session, db_user.id, content)
        await session.flush()

    tz = db_user.timezone or "UTC+8"
    snippet = content[:120] + ("..." if len(content) > 120 else "")
    date_str = format_entry_date_local(entry.created_at, tz)
    ack = random.choice(ENTRY_SAVED_RESPONSES)

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"{EMOJI_DELETE} Delete", callback_data=f"del:{entry.id}")]]
    )
    await update.effective_message.reply_text(
        f'{ack}\n\n"{_escape_md(snippet)}"\n\n_{_escape_md(date_str)}_',
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
