from fastapi import APIRouter, HTTPException, Request, status
from telegram import Update

from app.telegram.bot import get_application

router = APIRouter(tags=["telegram"])


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> dict:
    bot = get_application()
    data = await request.json()

    update = Update.de_json(data, bot.bot)
    if update is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid update",
        )

    await bot.process_update(update)
    return {"ok": True}
