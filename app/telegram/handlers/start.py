
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    complete_onboarding,
    get_or_create_preferences,
    get_or_create_user,
    get_session,
)

TIMEZONE_OFFSETS = [
    ("UTC-12", "UTC-12"),
    ("UTC-11", "UTC-11"),
    ("UTC-10", "UTC-10"),
    ("UTC-9", "UTC-9"),
    ("UTC-8 (PST)", "UTC-8"),
    ("UTC-7 (MST)", "UTC-7"),
    ("UTC-6 (CST)", "UTC-6"),
    ("UTC-5 (EST)", "UTC-5"),
    ("UTC-4", "UTC-4"),
    ("UTC-3", "UTC-3"),
    ("UTC-2", "UTC-2"),
    ("UTC-1", "UTC-1"),
    ("UTC", "UTC"),
    ("UTC+1 (CET)", "UTC+1"),
    ("UTC+2 (EET)", "UTC+2"),
    ("UTC+3", "UTC+3"),
    ("UTC+4", "UTC+4"),
    ("UTC+5", "UTC+5"),
    ("UTC+5:30 (IST)", "UTC+5:30"),
    ("UTC+6", "UTC+6"),
    ("UTC+7", "UTC+7"),
    ("UTC+8 (SGT/HKT)", "UTC+8"),
    ("UTC+9 (JST)", "UTC+9"),
    ("UTC+10", "UTC+10"),
    ("UTC+11", "UTC+11"),
    ("UTC+12", "UTC+12"),
]


async def start_command(
    update: Update, _context: CallbackContext
) -> None:
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

        if pref.onboarding_completed:
            await update.message.reply_text(
                f"Welcome back, {user.first_name}! "
                "You're all set. Use /grateful to write an entry."
            )
            return

        await session.commit()

    keyboard = [
        [
            InlineKeyboardButton(
                "📍 Send Location", callback_data="onboard_location"
            ),
            InlineKeyboardButton(
                "🔧 Set Manually", callback_data="onboard_manual"
            ),
        ]
    ]
    await update.message.reply_text(
        f"Welcome to Gratitude Jar, {user.first_name}! 🫙\n\n"
        "First, let's set your timezone so I can send you "
        "messages at the right time.\n\n"
        "How would you like to set it?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def onboard_location_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [[
        InlineKeyboardButton(
            "📍 Share Location", callback_data="onboard_share_location"
        )
    ]]
    await query.edit_message_text(
        "Tap the button below to share your location, "
        "then I'll detect your timezone automatically.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def onboard_manual_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = []
    for label, tz in TIMEZONE_OFFSETS:
        keyboard.append([InlineKeyboardButton(label, callback_data=f"tz:{tz}")])

    await query.edit_message_text(
        "Select your timezone:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def location_callback(
    update: Update, _context: CallbackContext
) -> None:
    message = update.message
    if not message.location:
        return

    from app.infrastructure.timezone import get_timezone
    from pytz import timezone as tz_module
    import datetime

    tz_name = await get_timezone(
        lat=message.location.latitude,
        lng=message.location.longitude,
    )

    offset_str = "UTC"
    if tz_name:
        try:
            tz_obj = tz_module(tz_name)
            offset = datetime.datetime.now(tz_obj).utcoffset().total_seconds() / 3600
            hours = int(offset)
            minutes = int((abs(offset) - abs(hours)) * 60)
            sign = "+" if offset >= 0 else "-"
            if minutes:
                offset_str = f"UTC{sign}{abs(hours):.0f}:{minutes:02d}"
            else:
                offset_str = f"UTC{sign}{abs(hours):.0f}"
        except Exception:
            offset_str = "UTC"

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=message.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        pref.timezone = offset_str
        await session.commit()

    keyboard = [
        [
            InlineKeyboardButton("✅ All of them", callback_data="prefs:all"),
            InlineKeyboardButton("🔧 Choose", callback_data="prefs:choose"),
        ]
    ]
    await message.reply_text(
        f"Timezone set to {offset_str}. Now let's set your preferences.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def timezone_selected_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    data = query.data
    tz = data.split(":", 1)[1]

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        pref.timezone = tz
        await session.commit()

    keyboard = [
        [
            InlineKeyboardButton("✅ All of them", callback_data="prefs:all"),
            InlineKeyboardButton("🔧 Choose", callback_data="prefs:choose"),
        ]
    ]
    await query.edit_message_text(
        f"Timezone set to {tz}. Now let's set your preferences.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def prefs_all_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        pref.digest_weekly_enabled = True
        pref.digest_monthly_enabled = True
        pref.digest_yearly_enabled = True
        pref.reminder_enabled = True
        pref.rediscovery_enabled = True
        await complete_onboarding(session, db_user.id)
        await session.commit()

    await query.edit_message_text(
        "All set! Here's what you've enabled:\n\n"
        "⏰ Evening reminder (if no entry today)\n"
        "📅 Weekly digest (Sunday)\n"
        "📅 Monthly digest (last day)\n"
        "📅 Yearly digest (Dec 31)\n"
        "🎁 Random rediscovery (4-6x/week)\n\n"
        "Try /grateful to write your first entry!"
    )


async def prefs_choose_callback(
    update: Update, context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    context.chat_data["onboard_prefs"] = {
        "weekly": True,
        "monthly": True,
        "yearly": True,
        "reminder": True,
        "rediscovery": True,
    }

    keyboard = [
        [InlineKeyboardButton("✅ Daily Reminder", callback_data="toggle:reminder")],
        [InlineKeyboardButton("✅ Weekly Digest", callback_data="toggle:weekly")],
        [InlineKeyboardButton("✅ Monthly Digest", callback_data="toggle:monthly")],
        [InlineKeyboardButton("✅ Yearly Digest", callback_data="toggle:yearly")],
        [InlineKeyboardButton("✅ Rediscovery", callback_data="toggle:rediscovery")],
        [InlineKeyboardButton("💾 Done", callback_data="prefs:done")],
    ]
    await query.edit_message_text(
        "Tap to toggle each preference:\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def toggle_preference_callback(
    update: Update, context: CallbackContext
) -> None:
    query = update.callback_query
    data = query.data
    key = data.split(":", 1)[1]

    prefs = context.chat_data.get("onboard_prefs", {})
    prefs[key] = not prefs.get(key, True)
    context.chat_data["onboard_prefs"] = prefs

    def emoji(val: bool) -> str:
        return "✅" if val else "❌"

    keyboard = [
        [InlineKeyboardButton(
            f"{emoji(prefs['reminder'])} Daily Reminder", callback_data="toggle:reminder"
        )],
        [InlineKeyboardButton(
            f"{emoji(prefs['weekly'])} Weekly Digest", callback_data="toggle:weekly"
        )],
        [InlineKeyboardButton(
            f"{emoji(prefs['monthly'])} Monthly Digest", callback_data="toggle:monthly"
        )],
        [InlineKeyboardButton(
            f"{emoji(prefs['yearly'])} Yearly Digest", callback_data="toggle:yearly"
        )],
        [InlineKeyboardButton(
            f"{emoji(prefs['rediscovery'])} Rediscovery", callback_data="toggle:rediscovery"
        )],
        [InlineKeyboardButton("💾 Done", callback_data="prefs:done")],
    ]

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.answer()


async def prefs_done_callback(
    update: Update, _context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    prefs = _context.chat_data.get("onboard_prefs", {})

    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=query.from_user.id)
        pref = await get_or_create_preferences(session, db_user.id)
        pref.reminder_enabled = prefs.get("reminder", True)
        pref.digest_weekly_enabled = prefs.get("weekly", True)
        pref.digest_monthly_enabled = prefs.get("monthly", True)
        pref.digest_yearly_enabled = prefs.get("yearly", True)
        pref.rediscovery_enabled = prefs.get("rediscovery", True)
        await complete_onboarding(session, db_user.id)
        await session.commit()

    await query.edit_message_text(
        "You're all set! Try /grateful to write your first entry."
    )
