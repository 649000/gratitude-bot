from telegram import Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    get_session,
    update_user,
)

TIMEZONE_MAP = {
    "UTC-12": "UTC-12",
    "UTC-11": "UTC-11",
    "UTC-10": "UTC-10",
    "UTC-9": "UTC-9",
    "UTC-8": "UTC-8",
    "UTC-7": "UTC-7",
    "UTC-6": "UTC-6",
    "UTC-5": "UTC-5",
    "UTC-4": "UTC-4",
    "UTC-3": "UTC-3",
    "UTC-2": "UTC-2",
    "UTC-1": "UTC-1",
    "UTC": "UTC",
    "UTC+1": "UTC+1",
    "UTC+2": "UTC+2",
    "UTC+3": "UTC+3",
    "UTC+4": "UTC+4",
    "UTC+5": "UTC+5",
    "UTC+5:30": "UTC+5:30",
    "UTC+6": "UTC+6",
    "UTC+7": "UTC+7",
    "UTC+8": "UTC+8",
    "UTC+9": "UTC+9",
    "UTC+10": "UTC+10",
    "UTC+11": "UTC+11",
    "UTC+12": "UTC+12",
}


async def timezone_command(update: Update, _context: CallbackContext) -> None:
    args = _context.args if _context.args else []

    if not args:
        await update.message.reply_text(
            "Usage: /timezone UTC+8\n\nSupported formats: UTC-12 to UTC+12 (e.g. UTC+8, UTC-5, UTC)"
        )
        return

    tz_input = " ".join(args)
    tz = tz_input.upper().replace(" ", "")

    if tz not in TIMEZONE_MAP:
        await update.message.reply_text(
            f"Invalid timezone: {tz_input}\n\nSupported: UTC-12 to UTC+12 (e.g. UTC+8, UTC-5, UTC)"
        )
        return

    tz = TIMEZONE_MAP[tz]

    async with get_session() as session:
        await update_user(session, telegram_id=update.effective_user.id, timezone=tz)
        await session.commit()

    await update.message.reply_text(f"Timezone set to {tz}")
