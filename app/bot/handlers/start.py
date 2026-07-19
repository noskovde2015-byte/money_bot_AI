from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import main_keyboard
from app.db.user import User

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, user: User):
    text = (
        "👋 Привет! Я помогу тебе вести учёт финансов.\n\n"
        "Вот что я умею:\n\n"
        "💸 <b>Внести трату</b> — просто опиши покупку своими словами, "
        "например: «потратил 500 в магните на чипсы». Я сам определю категорию "
        "и помечу, если трата нежелательная (фастфуд, алкоголь, азартные игры и т.д.)\n\n"
        "💰 <b>Внести доход</b> — укажи сумму, которую получил\n\n"
        "📊 <b>Отчёт за месяц</b> — покажу траты по категориям, сравнение с прошлым "
        "месяцем и дам небольшой совет\n\n"
        "Выбирай действие на клавиатуре ниже 👇"
    )
    await message.answer(text, reply_markup=main_keyboard, parse_mode="HTML")
