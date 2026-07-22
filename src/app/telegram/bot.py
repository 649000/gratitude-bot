import html
import logging
import traceback

from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.telegram.handlers.callbacks import delete_callback, star_callback
from app.telegram.handlers.entries import (
    entries_all_year_callback,
    entries_command,
    entries_month_callback,
    entries_page_callback,
    entries_year_callback,
)
from app.telegram.handlers.export import export_command
from app.telegram.handlers.grateful import grateful_command, save_entry_handler
from app.telegram.handlers.help import help_command
from app.telegram.handlers.settings import (
    settings_command,
    settings_timezone_callback,
    settings_toggle_callback,
)
from app.telegram.handlers.stars import (
    star_page_callback,
    star_unstar_callback,
    stars_command,
)
from app.telegram.handlers.start import (
    location_callback,
    onboard_location_callback,
    onboard_manual_callback,
    prefs_all_callback,
    prefs_choose_callback,
    prefs_done_callback,
    start_command,
    timezone_selected_callback,
    toggle_preference_callback,
)
from app.telegram.handlers.stats import stats_command
from app.telegram.handlers.surprise import surprise_command
from app.telegram.handlers.timezone_handler import timezone_command, timezone_quick_callback
from app.telegram.messages import NOT_TEXT_MESSAGE, UNKNOWN_COMMAND

logger = logging.getLogger(__name__)

_application: Application | None = None


def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("grateful", grateful_command))
    app.add_handler(CommandHandler("surprise", surprise_command))
    app.add_handler(CommandHandler("entries", entries_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("timezone", timezone_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("star", stars_command))

    app.add_handler(CallbackQueryHandler(onboard_location_callback, pattern="^onboard_location$"))
    app.add_handler(CallbackQueryHandler(onboard_manual_callback, pattern="^onboard_manual$"))
    app.add_handler(MessageHandler(filters.LOCATION, location_callback))
    app.add_handler(CallbackQueryHandler(timezone_selected_callback, pattern="^tz:"))
    app.add_handler(CallbackQueryHandler(prefs_all_callback, pattern="^prefs:all$"))
    app.add_handler(CallbackQueryHandler(prefs_choose_callback, pattern="^prefs:choose$"))
    app.add_handler(CallbackQueryHandler(prefs_done_callback, pattern="^prefs:done$"))
    app.add_handler(CallbackQueryHandler(toggle_preference_callback, pattern="^toggle:"))

    app.add_handler(CallbackQueryHandler(entries_year_callback, pattern="^y:"))
    app.add_handler(CallbackQueryHandler(entries_month_callback, pattern="^m:"))
    app.add_handler(CallbackQueryHandler(entries_all_year_callback, pattern="^ay:"))
    app.add_handler(CallbackQueryHandler(entries_page_callback, pattern="^ep:"))
    app.add_handler(CallbackQueryHandler(entries_page_callback, pattern="^ayp:"))
    app.add_handler(CallbackQueryHandler(entries_month_callback, pattern="^dy:"))

    app.add_handler(CallbackQueryHandler(settings_toggle_callback, pattern="^s:"))
    app.add_handler(CallbackQueryHandler(settings_timezone_callback, pattern="^tzp:"))

    app.add_handler(CallbackQueryHandler(star_callback, pattern="^star:"))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^del:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_entry_handler))

    app.add_handler(MessageHandler(filters.COMMAND, _unknown_command_handler))
    app.add_handler(MessageHandler(~filters.TEXT, _non_text_handler))
    app.add_handler(CallbackQueryHandler(_nav_callback, pattern="^nav:"))
    app.add_handler(CallbackQueryHandler(timezone_quick_callback, pattern="^tzq:"))
    app.add_handler(CallbackQueryHandler(star_page_callback, pattern="^star_p:"))
    app.add_handler(CallbackQueryHandler(star_unstar_callback, pattern="^staru:"))

    app.add_error_handler(error_handler)

    return app


async def _unknown_command_handler(update: Update, context: CallbackContext) -> None:
    await update.effective_message.reply_text(UNKNOWN_COMMAND)


async def _non_text_handler(update: Update, context: CallbackContext) -> None:
    await update.effective_message.reply_text(NOT_TEXT_MESSAGE)


async def _nav_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    target = query.data.split(":", 1)[1] if query.data else ""

    if target == "entries":
        from app.telegram.handlers.entries import entries_command

        await entries_command(update, context)
    elif target == "settings":
        from app.telegram.handlers.settings import settings_command

        await settings_command(update, context)
    elif target == "stats":
        from app.telegram.handlers.stats import stats_command

        await stats_command(update, context)
    elif target == "grateful":
        from app.telegram.handlers.grateful import grateful_command

        await grateful_command(update, context)
    elif target == "star":
        from app.telegram.handlers.stars import stars_command

        await stars_command(update, context)
    elif target == "surprise":
        from app.telegram.handlers.surprise import surprise_command

        await surprise_command(update, context)


async def error_handler(update: object, context: CallbackContext) -> None:
    error = context.error
    if error is None:
        logger.warning("error_handler called with no error")
        return
    if not hasattr(error, "__traceback__") or error.__traceback__ is None:
        logger.error("Unhandled exception: %s", error, exc_info=error)
        return

    tb_text = "".join(traceback.format_exception(None, error, error.__traceback__))
    tb_short = tb_text[:2500]

    msg = f"<b>⚠️ {html.escape(type(error).__name__)}</b>\n<pre>{html.escape(tb_short)}</pre>"
    if update and isinstance(update, Update):
        update_str = html.escape(str(update)[:800])
        msg += f"\n<b>Update:</b>\n<pre>{update_str}</pre>"

    logger.error("Unhandled exception: %s", error, exc_info=error)

    # Try HTML first, fall back to plain text if HTML causes Telegram rejection
    for parse_mode, text in [("HTML", msg), (None, _strip_html(msg))]:
        try:
            if update and isinstance(update, Update) and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=_GENERIC_ERROR,
                )
            await context.bot.send_message(
                chat_id=settings.telegram_error_chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            break
        except Exception:
            pass
    else:
        logger.error("Failed to send error notification via Telegram")


_GENERIC_ERROR = "Oops! Something went wrong on my end. The team has been notified \U0001f6e0\ufe0f"


def _strip_html(text: str) -> str:
    import re

    return re.sub(r"<[^>]+>", "", text)


async def get_application() -> Application:
    global _application
    if _application is None:
        _application = build_application()
        await _application.initialize()
    return _application
