from datetime import UTC, datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_entry_count,
    get_entry_count_range,
    get_first_entry_date,
    get_or_create_user,
    get_session,
    get_starred_count,
    get_streak,
)
from app.telegram.messages import (
    STATS_BTN_ENTRIES,
    STATS_BTN_SETTINGS,
    STATS_TEMPLATE,
    format_digest_date,
)


def _week_range():
    now = datetime.now(UTC)
    monday = now - timedelta(days=now.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _month_range():
    now = datetime.now(UTC)
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return first


async def stats_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        total = await get_entry_count(session, db_user.id)
        week = await get_entry_count_range(session, db_user.id, _week_range())
        month = await get_entry_count_range(session, db_user.id, _month_range())
        starred = await get_starred_count(session, db_user.id)
        streak = await get_streak(session, db_user.id)
        first = await get_first_entry_date(session, db_user.id)

    since_text = "—"
    if first:
        days = (datetime.now(UTC) - first.replace(tzinfo=UTC)).days
        since_text = f"{format_digest_date(first)} ({days} days ago)"

    text = STATS_TEMPLATE.format(
        total=total,
        week=week,
        month=month,
        starred=starred,
        streak=streak,
        since=since_text,
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(STATS_BTN_ENTRIES, callback_data="nav:entries"),
                InlineKeyboardButton(STATS_BTN_SETTINGS, callback_data="nav:settings"),
            ]
        ]
    )

    await update.effective_message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
