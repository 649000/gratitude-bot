from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import get_or_create_user, get_session
from app.telegram.messages import EMOJI_LOCATION, TZ_COMMON_OFFSETS, TZ_INVALID, TZ_PROMPT, TZ_SET


async def timezone_command(update: Update, context: CallbackContext) -> None:
    args = context.args
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        current_tz = db_user.timezone or "UTC+8"

    if args:
        tz = args[0]
        valid_offsets = (
            {f"UTC{-i}" for i in range(-12, 13)} | {f"UTC+{i}" for i in range(0, 13)} | {"UTC"}
        )
        if tz not in valid_offsets:
            await update.effective_message.reply_text(TZ_INVALID.format(tz_input=tz))
            return

        db_user.timezone = tz
        await session.commit()
        await update.effective_message.reply_text(TZ_SET.format(tz=tz))
        return

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

    await update.effective_message.reply_text(
        TZ_PROMPT.format(tz=current_tz),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def timezone_quick_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    tz = query.data.split(":", 1)[1]

    async with get_session() as session:
        user = await get_or_create_user(
            session,
            telegram_id=query.from_user.id,
            username=query.from_user.username,
            first_name=query.from_user.first_name,
            last_name=query.from_user.last_name,
        )
        user.timezone = tz
        await session.commit()

    await query.edit_message_text(TZ_SET.format(tz=tz))
