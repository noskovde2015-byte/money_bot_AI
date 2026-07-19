from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_year_selection_keyboard
from app.finance.report_service import build_yearly_overview
from app.db.user import User

router = Router()


@router.message(F.text == "Годовой отчёт")
async def handle_yearly_report_request(message: Message):
    year = datetime.now().year
    last_year = year - 1

    years = [year, last_year]

    text = "Отчёт за какой год тебе интересен?"

    await message.answer(text, reply_markup=get_year_selection_keyboard(years))


@router.callback_query(F.data.startswith("yearly_report:"))
async def handle_year_selected(
    callback: CallbackQuery, user: User, session: AsyncSession
):
    year = int(callback.data.split(":")[1])

    overview = await build_yearly_overview(user_id=user.id, session=session, year=year)

    lines = [
        f"<b>{month['month_name'].capitalize()}</b>\n"
        f"  💰 Доходы: {month['incomes']}₽\n"
        f"  💸 Траты: {month['expenses']}₽\n"
        f"  ⚖️ Дельта: {month['delta']}₽\n"
        f"  ⚠️ Нежелательные: {month['harmful']}₽"
        for month in overview
    ]
    text = "📅 <b>Годовой отчёт</b>\n\n" + "\n\n".join(lines)
    await callback.message.answer(text, parse_mode="html")
    await callback.answer()
