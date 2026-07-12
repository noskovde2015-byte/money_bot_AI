from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user import User
from app.bot.states import IncomeStates
from app.finance.income_service import process_income

router = Router()


@router.message(F.text == "Внести доход")
async def start_income_input(message: Message, state: FSMContext):
    await message.answer("Введите свой доход (число), например: 50000")
    await state.set_state(IncomeStates.waiting_for_income_amount)


@router.message(IncomeStates.waiting_for_income_amount)
async def handle_income_amount(
    message: Message, user: User, state: FSMContext, session: AsyncSession
):
    try:
        income = await process_income(
            user_id=user.id, raw_text=message.text, session=session
        )
    except ValueError:
        await message.answer(
            "Похоже, это не число. Введите доход в виде числа, например: 50000"
        )
        return

    await message.answer(f"Записал доход: {income.amount}₽")
    await state.clear()
