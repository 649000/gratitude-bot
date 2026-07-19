from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_or_create_preferences,
    get_or_create_user,
    get_session,
)


async def settings_command(
    update: Update, _context: CallbackContext
) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        await session.commit()

    keyboard = [
        [InlineKeyboardButton(
            f"{'✅' if pref.reminder_enabled else '❌'} Daily Reminder",
            callback_data="s:reminder",
        )],
        [InlineKeyboardButton(
            f"{'✅' if pref.digest_weekly_enabled else '❌'} Weekly Digest",
            callback_data="s:weekly",
        )],
        [InlineKeyboardButton(
            f"{'✅' if pref.digest_monthly_enabled else '❌'} Monthly Digest",
            callback_data="s:monthly",
        )],
        [InlineKeyboardButton(
            f"{'✅' if pref.digest_yearly_enabled else '❌'} Yearly Digest",
            callback_data="s:yearly",
        )],
        [InlineKeyboardButton(
            f"{'✅' if pref.rediscovery_enabled else '❌'} Rediscovery",
            callback_data="s:rediscovery",
        )],
        [InlineKeyboardButton(
            f"📍 Timezone: {pref.timezone or 'UTC+8'}",
            callback_data="s:timezone",
        )],
    ]
    await update.message.reply_text(
        "⚙️ Your preferences:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def settings_toggle_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    key = query.data.split(":", 1)[1]
    await query.answer()

    if key == "timezone":
        from app.telegram.handlers.start import (
            TIMEZONE_OFFSETS,
        )

        keyboard = []
        for label, tz in TIMEZONE_OFFSETS:
            keyboard.append([InlineKeyboardButton(label, callback_data=f"stz:{tz}")])

        await query.edit_message_text(
            "Select your timezone:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    field_map = {
        "reminder": "reminder_enabled",
        "weekly": "digest_weekly_enabled",
        "monthly": "digest_monthly_enabled",
        "yearly": "digest_yearly_enabled",
        "rediscovery": "rediscovery_enabled",
    }

    field = field_map.get(key)
    if not field:
        return

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        current = getattr(pref, field)
        setattr(pref, field, not current)
        await session.commit()

        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if pref.reminder_enabled else '❌'} Daily Reminder",
                callback_data="s:reminder",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_weekly_enabled else '❌'} Weekly Digest",
                callback_data="s:weekly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_monthly_enabled else '❌'} Monthly Digest",
                callback_data="s:monthly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_yearly_enabled else '❌'} Yearly Digest",
                callback_data="s:yearly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.rediscovery_enabled else '❌'} Rediscovery",
                callback_data="s:rediscovery",
            )],
            [InlineKeyboardButton(
                f"📍 Timezone: {pref.timezone or 'UTC+8'}",
                callback_data="s:timezone",
            )],
        ]

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def settings_timezone_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    tz = query.data.split(":", 1)[1]
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        pref.timezone = tz
        await session.commit()

        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if pref.reminder_enabled else '❌'} Daily Reminder",
                callback_data="s:reminder",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_weekly_enabled else '❌'} Weekly Digest",
                callback_data="s:weekly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_monthly_enabled else '❌'} Monthly Digest",
                callback_data="s:monthly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.digest_yearly_enabled else '❌'} Yearly Digest",
                callback_data="s:yearly",
            )],
            [InlineKeyboardButton(
                f"{'✅' if pref.rediscovery_enabled else '❌'} Rediscovery",
                callback_data="s:rediscovery",
            )],
            [InlineKeyboardButton(
                f"📍 Timezone: {tz}",
                callback_data="s:timezone",
            )],
        ]

    await query.edit_message_text(
        f"Timezone updated to {tz}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
