from telegram import Update
from telegram.ext import Application, CommandHandler

from app.config import settings

_application: Application | None = None


async def start_command(update: Update, _context: None) -> None:
    await update.message.reply_text("Welcome! Send me what you're grateful for and I'll save it.")


async def grateful_command(update: Update, _context: None) -> None:
    await update.message.reply_text("Tell me what you're grateful for by sending a message.")


def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("grateful", grateful_command))
    return app


def get_application() -> Application:
    global _application
    if _application is None:
        _application = build_application()
    return _application
