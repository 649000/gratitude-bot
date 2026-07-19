import json
from io import BytesIO

from telegram import Update
from telegram.ext import CallbackContext

from app.telegram.handlers.db import (
    export_entries,
    get_or_create_user,
    get_session,
)


async def export_command(
    update: Update, _context: CallbackContext
) -> None:
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_or_create_user(session, telegram_id=user.id)
        entries = await export_entries(session, db_user.id)
        await session.commit()

    if not entries:
        await update.message.reply_text(
            "Your jar is empty. Write something first with /grateful 🫙"
        )
        return

    data = [
        {
            "date": e.created_at.isoformat(),
            "content": e.content,
            "starred": e.starred,
        }
        for e in entries
    ]

    file_content = json.dumps(data, indent=2, ensure_ascii=False)
    file = BytesIO(file_content.encode("utf-8"))
    file.name = f"gratitude-export-{user.id}.json"

    await update.message.reply_document(
        document=file,
        caption=f"📦 {len(entries)} entries exported",
    )
