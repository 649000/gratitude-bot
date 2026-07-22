import io
import json

from telegram import Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import export_entries, get_or_create_user, get_session
from app.telegram.messages import EXPORT_EMPTY, EXPORT_SUCCESS


def _build_export(entries) -> str:
    items = []
    for e in entries:
        items.append(
            {
                "id": str(e.id),
                "content": e.content,
                "source": e.source,
                "starred": e.starred,
                "date": e.created_at.isoformat(),
                "date_human": e.created_at.strftime("%d %b %Y, %-I:%M %p"),
            }
        )
    return json.dumps(items, indent=2, ensure_ascii=False)


async def export_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        entries = await export_entries(session, db_user.id)

    if not entries:
        await update.effective_message.reply_text(EXPORT_EMPTY)
        return

    data = _build_export(entries)
    buf = io.BytesIO(data.encode("utf-8"))
    buf.name = f"gratitude_jar_export_{db_user.id}.json"
    await update.effective_message.reply_document(
        buf,
        caption=EXPORT_SUCCESS.format(count=len(entries)),
    )
