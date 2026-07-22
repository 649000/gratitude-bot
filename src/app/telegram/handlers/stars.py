import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_or_create_user,
    get_session,
    get_starred_count,
    get_starred_entries,
    star_entry,
)
from app.telegram.messages import (
    EMOJI_NEXT,
    EMOJI_PREV,
    EMOJI_STAR,
    STARS_EMPTY,
    STARS_HEADER,
    _escape_md,
    format_entry_date_local,
)

_PAGE_SIZE = 5


async def _resolve_user(session, update):
    user = update.effective_user
    return await get_or_create_user(
        session,
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def _build_page_text(entries, page: int, tz: str, total: int) -> str:
    shown = min(page + _PAGE_SIZE, total)
    text = STARS_HEADER.format(shown=shown, total=total)
    for i, e in enumerate(entries):
        num = page + i + 1
        date_str = format_entry_date_local(e.created_at, tz)
        snippet = e.content[:80] + ("..." if len(e.content) > 80 else "")
        text += f'{num}. "{_escape_md(snippet)}"\n'
        text += f"   \u2014 {_escape_md(date_str)}\n\n"
    return text


def _build_nav_keyboard(entries, page: int, total: int):
    keyboard = []
    for i, e in enumerate(entries):
        num = page + i + 1
        label = f"{EMOJI_STAR} Unstar {num}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"staru:{e.id}:{page}")])
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(f"{EMOJI_PREV} Prev", callback_data=f"star_p:{page - _PAGE_SIZE}")
        )
    if page + _PAGE_SIZE < total:
        nav.append(
            InlineKeyboardButton(f"{EMOJI_NEXT} Next", callback_data=f"star_p:{page + _PAGE_SIZE}")
        )
    if nav:
        keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)


async def stars_command(update: Update, context: CallbackContext) -> None:
    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await get_starred_count(session, db_user.id)
        entries = await get_starred_entries(session, db_user.id, limit=_PAGE_SIZE, offset=0)

    if not entries:
        await update.effective_message.reply_text(STARS_EMPTY)
        return

    text = _build_page_text(entries, 0, tz, total)
    reply_markup = _build_nav_keyboard(entries, 0, total)
    await update.effective_message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def star_page_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    page = int(query.data.split(":")[1])

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await get_starred_count(session, db_user.id)
        entries = await get_starred_entries(session, db_user.id, limit=_PAGE_SIZE, offset=page)

    if not entries and page > 0:
        page = max(0, page - _PAGE_SIZE)
        async with get_session() as session:
            entries = await get_starred_entries(session, db_user.id, limit=_PAGE_SIZE, offset=page)

    if not entries:
        await query.edit_message_text(STARS_EMPTY)
        return

    text = _build_page_text(entries, page, tz, total)
    reply_markup = _build_nav_keyboard(entries, page, total)
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def star_unstar_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    parts = query.data.split(":")
    entry_id = uuid.UUID(parts[1])
    page = int(parts[2])

    async with get_session() as session:
        await star_entry(session, entry_id, starred=False)
        await session.commit()

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await get_starred_count(session, db_user.id)
        entries = await get_starred_entries(session, db_user.id, limit=_PAGE_SIZE, offset=page)

    if not entries and page > 0:
        page = max(0, page - _PAGE_SIZE)
        async with get_session() as session:
            entries = await get_starred_entries(session, db_user.id, limit=_PAGE_SIZE, offset=page)

    if not entries:
        await query.edit_message_text(STARS_EMPTY)
        return

    text = _build_page_text(entries, page, tz, total)
    reply_markup = _build_nav_keyboard(entries, page, total)
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
