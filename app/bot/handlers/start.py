from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import main_keyboard
from app.db.user import User

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, user: User):
    await message.answer(
        "Привет! Я помогу тебе вести учёт финансов.",
        reply_markup=main_keyboard,
    )
