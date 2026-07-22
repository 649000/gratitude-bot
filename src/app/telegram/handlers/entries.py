from collections import defaultdict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    count_entries_filtered,
    get_distinct_months,
    get_distinct_years,
    get_entries,
    get_or_create_user,
    get_session,
)
from app.telegram.messages import (
    EMOJI_CALENDAR,
    EMOJI_NEXT,
    EMOJI_PREV,
    EMOJI_STAR,
    ENTRIES_PAGE_HEADER,
    JAR_EMPTY,
    MONTH_SELECT,
    NO_ENTRIES_PERIOD,
    NO_MORE_ENTRIES,
    YEAR_SELECT,
    _escape_md,
    format_entry_date_local,
    format_entry_date_short,
)


async def _safe_edit(query, text, **kwargs):
    try:
        await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise


_MONTH_SHORT = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
_MONTH_FULL = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


async def _resolve_user(session, update):
    user = update.effective_user
    return await get_or_create_user(
        session,
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def _group_by_day(entries, tz: str) -> list[tuple[str, list]]:
    groups: dict[str, list] = defaultdict(list)
    for e in entries:
        day_label = format_entry_date_short(e.created_at, tz)
        groups[day_label].append(e)
    return list(groups.items())


def _render_entries(entries, tz: str, show_day_header: bool = True) -> str:
    if show_day_header and entries:
        grouped = _group_by_day(entries, tz)
        lines = []
        for day_label, day_entries in grouped:
            lines.append(f"*{day_label}*")
            for e in day_entries:
                star = f"{EMOJI_STAR} " if e.starred else "     "
                snippet = e.content[:70] + ("..." if len(e.content) > 70 else "")
                lines.append(f'{star}"{_escape_md(snippet)}"')
            lines.append("")
        return "\n".join(lines)
    else:
        lines = []
        for e in entries:
            star = EMOJI_STAR if e.starred else ""
            date_str = format_entry_date_local(e.created_at, tz)
            snippet = e.content[:70] + ("..." if len(e.content) > 70 else "")
            lines.append(f"{_escape_md(date_str)} \u00b7 {star} {_escape_md(snippet)}")
        return "\n".join(lines)


async def entries_command(update: Update, context: CallbackContext) -> None:
    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        years = await get_distinct_years(session, db_user.id)

    if not years:
        await update.effective_message.reply_text(JAR_EMPTY)
        return

    keyboard = [[InlineKeyboardButton(str(y), callback_data=f"y:{y}")] for y in years]
    await update.effective_message.reply_text(
        YEAR_SELECT,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def entries_year_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    year = int(query.data.split(":", 1)[1])

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        months = await get_distinct_months(session, db_user.id, year)

    if not months:
        await _safe_edit(query, NO_ENTRIES_PERIOD.format(period=str(year)))
        return

    keyboard = []
    for m in months:
        keyboard.append([InlineKeyboardButton(_MONTH_SHORT[m], callback_data=f"m:{year}:{m}")])
    keyboard.append(
        [InlineKeyboardButton(f"{EMOJI_CALENDAR} All Year", callback_data=f"ay:{year}")]
    )

    await _safe_edit(
        query,
        MONTH_SELECT.format(year=year),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def entries_month_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    year = int(parts[1])
    month = int(parts[2])

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await count_entries_filtered(session, db_user.id, year=year, month=month)
        entries = await get_entries(session, db_user.id, year=year, month=month, limit=10, offset=0)

    if not entries:
        await _safe_edit(query, NO_ENTRIES_PERIOD.format(period=f"{_MONTH_FULL[month]} {year}"))
        return

    page_size = 10
    pages = max(1, (total + page_size - 1) // page_size)
    label = f"{_MONTH_FULL[month]} {year}"
    header = ENTRIES_PAGE_HEADER.format(label=label, count=total, page=1, pages=pages)
    body = _render_entries(entries[:page_size], tz, show_day_header=True)
    text = header + body

    keyboard = []
    if total > page_size:
        keyboard.append(
            [InlineKeyboardButton(f"{EMOJI_NEXT} Next", callback_data=f"ep:{year}:{month}:10")]
        )

    await _safe_edit(
        query,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def entries_page_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    year = int(parts[1])
    month = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else 0
    offset = int(parts[-1])
    page_size = 10

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await count_entries_filtered(
            session, db_user.id, year=year, month=month if month else None
        )
        entries = await get_entries(
            session,
            db_user.id,
            year=year,
            month=month if month else None,
            limit=page_size + 1,
            offset=offset,
        )

    if not entries:
        await _safe_edit(query, NO_MORE_ENTRIES)
        return

    has_next = len(entries) > page_size
    if has_next:
        entries = entries[:page_size]

    page = offset // page_size + 1
    pages = max(1, (total + page_size - 1) // page_size)

    label = f"{_MONTH_FULL[month]} {year}" if month else str(year)
    header = ENTRIES_PAGE_HEADER.format(label=label, count=total, page=page, pages=pages)
    body = _render_entries(entries, tz, show_day_header=bool(month))
    text = header + body

    keyboard = []
    nav = []
    if offset > 0:
        nav.append(
            InlineKeyboardButton(
                f"{EMOJI_PREV} Prev",
                callback_data=f"ep:{year}:{month or 0}:{offset - page_size}",
            )
        )
    if has_next:
        nav.append(
            InlineKeyboardButton(
                f"{EMOJI_NEXT} Next",
                callback_data=f"ep:{year}:{month or 0}:{offset + page_size}",
            )
        )
    if nav:
        keyboard.append(nav)

    await _safe_edit(
        query,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def entries_all_year_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    year = int(parts[1])

    async with get_session() as session:
        db_user = await _resolve_user(session, update)
        tz = db_user.timezone or "UTC+8"
        total = await count_entries_filtered(session, db_user.id, year=year)
        entries = await get_entries(session, db_user.id, year=year, limit=10)

    if not entries:
        await _safe_edit(query, NO_ENTRIES_PERIOD.format(period=str(year)))
        return

    page_size = 10
    pages = max(1, (total + page_size - 1) // page_size)
    label = str(year)
    header = ENTRIES_PAGE_HEADER.format(label=label, count=total, page=1, pages=pages)
    body = _render_entries(entries, tz, show_day_header=False)
    text = header + body

    keyboard = []
    if total > page_size:
        keyboard.append(
            [InlineKeyboardButton(f"{EMOJI_NEXT} Next", callback_data=f"ayp:{year}:0:10")]
        )

    await _safe_edit(
        query,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )
