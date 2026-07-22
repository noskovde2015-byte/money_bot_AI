from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, Request, Depends
from app.api.dependencies import get_bot, get_dispatcher

router = APIRouter()


@router.post("/webhook")
async def webhook(
    request: Request,
    bot: Bot = Depends(get_bot),
    dp: Dispatcher = Depends(get_dispatcher),
) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
