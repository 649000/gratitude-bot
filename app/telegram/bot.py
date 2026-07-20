from telegram.ext import (
    Application,
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
from app.telegram.handlers.surprise import surprise_command
from app.telegram.handlers.timezone_handler import timezone_command

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

    app.add_handler(CallbackQueryHandler(onboard_location_callback, pattern="^onboard_location$"))
    app.add_handler(CallbackQueryHandler(onboard_manual_callback, pattern="^onboard_manual$"))
    app.add_handler(CallbackQueryHandler(location_callback, pattern="^onboard_share_location$"))
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
    app.add_handler(CallbackQueryHandler(settings_timezone_callback, pattern="^stz:"))

    app.add_handler(CallbackQueryHandler(star_callback, pattern="^star:"))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^del:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_entry_handler))

    return app


async def get_application() -> Application:
    global _application
    if _application is None:
        _application = build_application()
        await _application.initialize()
    return _application
