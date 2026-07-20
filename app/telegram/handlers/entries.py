
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_distinct_days,
    get_distinct_months,
    get_distinct_years,
    get_entries,
    get_or_create_user,
    get_session,
)

ENTRIES_PER_PAGE = 5


async def entries_command(
    update: Update, _context: CallbackContext
) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=user.id)
        years = await get_distinct_years(session, db_user.id)
        await session.commit()

    if not years:
        await update.message.reply_text(
            "Your jar is empty! Write your first entry with /grateful 🫙"
        )
        return

    keyboard = [[InlineKeyboardButton(str(y), callback_data=f"y:{y}")] for y in years]
    await update.message.reply_text(
        "📅 Select a year:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def entries_year_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    year = int(query.data.split(":", 1)[1])
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        months = await get_distinct_months(session, db_user.id, year)
        await session.commit()

    if not months:
        await query.edit_message_text(f"No entries found for {year}.")
        return

    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    keyboard = [
        [InlineKeyboardButton(f"{month_names[m]}", callback_data=f"m:{year}:{m}")]
        for m in months
    ]
    keyboard.append([
        InlineKeyboardButton("📅 All Year", callback_data=f"ay:{year}")
    ])
    await query.edit_message_text(
        f"📅 Select a month in {year}:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def entries_month_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    _, year, month = query.data.split(":")
    year, month = int(year), int(month)
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        days = await get_distinct_days(session, db_user.id, year, month)
        entries = await get_entries(
            session, db_user.id, year=year, month=month, limit=ENTRIES_PER_PAGE
        )
        await session.commit()

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }

    if not entries:
        await query.edit_message_text(f"No entries found for {month_names[month]} {year}.")
        return

    text = f"📖 {month_names[month]} {year}:\n\n"
    for e in entries:
        text += f"• {e.content[:80]}{'...' if len(e.content) > 80 else ''}\n"

    keyboard = [
        [InlineKeyboardButton("▶️ Next", callback_data=f"ep:{year}:{month}:{ENTRIES_PER_PAGE}")]
        if len(entries) == ENTRIES_PER_PAGE
        else [],
        [InlineKeyboardButton("📅 By Day", callback_data=f"dy:{year}:{month}")]
        if days
        else [],
    ]
    keyboard = [row for row in keyboard if row]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )


async def entries_all_year_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    year = int(query.data.split(":", 1)[1])
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        entries = await get_entries(
            session, db_user.id, year=year, limit=ENTRIES_PER_PAGE
        )
        await session.commit()

    if not entries:
        await query.edit_message_text(f"No entries found for {year}.")
        return

    text = f"📖 {year}:\n\n"
    for e in entries:
        text += f"• {e.content[:80]}{'...' if len(e.content) > 80 else ''}\n"

    keyboard = [
        [InlineKeyboardButton("▶️ Next", callback_data=f"ayp:{year}:{ENTRIES_PER_PAGE}")]
        if len(entries) == ENTRIES_PER_PAGE
        else [],
    ]
    keyboard = [row for row in keyboard if row]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )


async def entries_page_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    parts = query.data.split(":")
    action = parts[0]
    await query.answer()

    if action == "ep":
        year, month, offset = int(parts[1]), int(parts[2]), int(parts[3])
    elif action == "ayp":
        year, month, offset = int(parts[1]), None, int(parts[2])
    else:
        return

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        entries = await get_entries(
            session, db_user.id, year=year, month=month,
            limit=ENTRIES_PER_PAGE, offset=offset,
        )
        await session.commit()

    if not entries:
        await query.edit_message_text("No more entries.")
        return

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }
    label = f"{month_names[month]} {year}" if month else str(year)
    text = f"📖 {label}:\n\n"
    for e in entries:
        text += f"• {e.content[:80]}{'...' if len(e.content) > 80 else ''}\n"

    keyboard = []
    if offset > 0:
        if month:
            data = f"ep:{year}:{month}:{max(0, offset - ENTRIES_PER_PAGE)}"
            keyboard.append([InlineKeyboardButton("◀️ Prev", callback_data=data)])
        else:
            data = f"ayp:{year}:{max(0, offset - ENTRIES_PER_PAGE)}"
            keyboard.append([InlineKeyboardButton("◀️ Prev", callback_data=data)])
    if len(entries) == ENTRIES_PER_PAGE:
        if month:
            data = f"ep:{year}:{month}:{offset + ENTRIES_PER_PAGE}"
            keyboard.append([InlineKeyboardButton("▶️ Next", callback_data=data)])
        else:
            data = f"ayp:{year}:{offset + ENTRIES_PER_PAGE}"
            keyboard.append([InlineKeyboardButton("▶️ Next", callback_data=data)])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )
