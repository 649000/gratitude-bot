from telegram import Update


async def help_command(update: Update, _context: None) -> None:
    await update.message.reply_text(
        "Here's what I can do:\n\n"
        "/grateful — Write a gratitude entry\n"
        "/surprise — Rediscover a random past entry\n"
        "/entries — Browse your gratitude jar\n"
        "/settings — View and toggle preferences\n"
        "/timezone — Change your timezone\n"
        "/export — Download all your entries\n"
        "/help — Show this message\n\n"
        "Send me what you're grateful for anytime!"
    )
