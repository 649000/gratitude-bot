import html
import json
import logging
import re
from contextlib import suppress

from telegram import InlineKeyboardMarkup

from app.config import settings
from app.telegram.bot import get_application

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


async def handle_sqs_records(records: list[dict]) -> dict:
    bot_app = await get_application()
    bot = bot_app.bot
    sent = 0
    failed = 0

    for record in records:
        try:
            body = json.loads(record["body"])
            chat_id = body["chat_id"]
            text = body["text"]
            parse_mode = body.get("parse_mode")
            reply_markup_data = body.get("reply_markup")

            kwargs = {}
            if parse_mode:
                kwargs["parse_mode"] = parse_mode
            if reply_markup_data:
                kwargs["reply_markup"] = InlineKeyboardMarkup.de_json(reply_markup_data, bot)

            await bot.send_message(
                chat_id=chat_id,
                text=text,
                **kwargs,
            )
            sent += 1
        except Exception:
            logger.exception("Failed to send SQS message to Telegram")
            failed += 1
            body_text = html.escape(str(record.get("body", ""))[:2000])
            msg_html = f"Failed SQS message:\n<pre>{body_text}</pre>"
            for parse_mode, text in [("HTML", msg_html), (None, _strip_html(msg_html))]:
                with suppress(Exception):
                    await bot.send_message(
                        chat_id=settings.telegram_error_chat_id,
                        text=text,
                        parse_mode=parse_mode,
                    )
                    break

    return {"sent": sent, "failed": failed}
