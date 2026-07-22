from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_entry_by_id,
    get_or_create_user,
    get_random_entry,
    get_session,
)
from app.telegram.messages import (
    EMOJI_DELETE,
    EMOJI_STAR,
    ENTRY_VANISHED,
    JAR_EMPTY,
    SURPRISE_PREFIX,
    _escape_md,
    format_entry_date_local,
)


async def surprise_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        entry = await get_random_entry(session, db_user.id)

    if not entry:
        await update.effective_message.reply_text(JAR_EMPTY)
        return

    tz = db_user.timezone or "UTC+8"
    date_str = format_entry_date_local(entry.created_at, tz)
    text = f'{SURPRISE_PREFIX}"{_escape_md(entry.content)}"\n\n_{_escape_md(date_str)}_'

    star_label = f"{EMOJI_STAR} Unstar" if entry.starred else f"{EMOJI_STAR} Star"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(star_label, callback_data=f"star:{entry.id}"),
                InlineKeyboardButton(f"{EMOJI_DELETE} Delete", callback_data=f"del:{entry.id}"),
            ]
        ]
    )

    await update.effective_message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def surprise_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    entry_id = query.data.split(":", 1)[1] if query.data else ""

    async with get_session() as session:
        entry = await get_entry_by_id(session, entry_id)

    if not entry:
        await query.answer(ENTRY_VANISHED)
        return

    tz = "UTC+8"
    try:
        from app.telegram.handlers.db import get_or_create_user as _gu

        async with get_session() as s:
            db_user = await _gu(
                s,
                telegram_id=query.from_user.id,
                username=query.from_user.username,
                first_name=query.from_user.first_name,
                last_name=query.from_user.last_name,
            )
            tz = db_user.timezone or "UTC+8"
    except Exception:
        pass

    date_str = format_entry_date_local(entry.created_at, tz)
    text = f'{SURPRISE_PREFIX}"{_escape_md(entry.content)}"\n\n_{_escape_md(date_str)}_'

    star_label = f"{EMOJI_STAR} Unstar" if entry.starred else f"{EMOJI_STAR} Star"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(star_label, callback_data=f"star:{entry.id}"),
                InlineKeyboardButton(f"{EMOJI_DELETE} Delete", callback_data=f"del:{entry.id}"),
            ]
        ]
    )

    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
