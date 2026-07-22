from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_or_create_preferences,
    get_or_create_user,
    get_session,
)
from app.telegram.messages import (
    EMOJI_CHECK,
    EMOJI_CROSS,
    EMOJI_LOCATION,
    SETTINGS_HEADER,
    TOGGLE_MONTHLY,
    TOGGLE_REDISCOVERY,
    TOGGLE_REMINDER,
    TOGGLE_TIMEZONE,
    TOGGLE_WEEKLY,
    TOGGLE_YEARLY,
    TZ_COMMON_OFFSETS,
    TZ_PROMPT,
    TZ_UPDATED,
)


def _build_toggle_row(
    key: str, label: str, enabled: bool, field: str
) -> list[InlineKeyboardButton]:
    icon = EMOJI_CHECK if enabled else EMOJI_CROSS
    return [InlineKeyboardButton(f"{icon} {label}", callback_data=f"s:{field}")]


async def settings_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        pref = await get_or_create_preferences(session, db_user.id)

    tz_value = db_user.timezone or "UTC+8"
    keyboard = [
        _build_toggle_row("reminder", TOGGLE_REMINDER, pref.reminder_enabled, "reminder"),
        _build_toggle_row("weekly", TOGGLE_WEEKLY, pref.digest_weekly_enabled, "digest_weekly"),
        _build_toggle_row("monthly", TOGGLE_MONTHLY, pref.digest_monthly_enabled, "digest_monthly"),
        _build_toggle_row("yearly", TOGGLE_YEARLY, pref.digest_yearly_enabled, "digest_yearly"),
        _build_toggle_row(
            "rediscovery", TOGGLE_REDISCOVERY, pref.rediscovery_enabled, "rediscovery"
        ),
        [
            InlineKeyboardButton(
                f"{EMOJI_LOCATION} {TOGGLE_TIMEZONE.format(tz=tz_value)}",
                callback_data="tzp:",
            )
        ],
    ]

    await update.effective_message.reply_text(
        SETTINGS_HEADER,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def settings_toggle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    field = query.data.split(":", 1)[1]

    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        pref = await get_or_create_preferences(session, db_user.id)

        current = getattr(pref, f"{field}_enabled", None)
        if current is not None:
            setattr(pref, f"{field}_enabled", not current)
            await session.commit()

        tz_value = db_user.timezone or "UTC+8"
        keyboard = [
            _build_toggle_row("reminder", TOGGLE_REMINDER, pref.reminder_enabled, "reminder"),
            _build_toggle_row("weekly", TOGGLE_WEEKLY, pref.digest_weekly_enabled, "digest_weekly"),
            _build_toggle_row(
                "monthly", TOGGLE_MONTHLY, pref.digest_monthly_enabled, "digest_monthly"
            ),
            _build_toggle_row("yearly", TOGGLE_YEARLY, pref.digest_yearly_enabled, "digest_yearly"),
            _build_toggle_row(
                "rediscovery", TOGGLE_REDISCOVERY, pref.rediscovery_enabled, "rediscovery"
            ),
            [
                InlineKeyboardButton(
                    f"{EMOJI_LOCATION} {TOGGLE_TIMEZONE.format(tz=tz_value)}",
                    callback_data="tzp:",
                )
            ],
        ]

    await query.edit_message_text(
        SETTINGS_HEADER,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def settings_timezone_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=query.from_user.id,
            username=query.from_user.username,
            first_name=query.from_user.first_name,
            last_name=query.from_user.last_name,
        )
        current_tz = db_user.timezone or "UTC+8"

    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI_LOCATION} Share Location",
                callback_data="onboard_location",
            )
        ],
    ]
    row = []
    for label, tz in TZ_COMMON_OFFSETS:
        row.append(InlineKeyboardButton(label, callback_data=f"tzq:{tz}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await query.edit_message_text(
        TZ_PROMPT.format(tz=current_tz),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def timezone_selected_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    tz = query.data.split(":", 1)[1]

    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        db_user.timezone = tz
        await session.commit()

    await query.edit_message_text(TZ_UPDATED.format(tz=tz))
