from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user import User
from app.bot.states import ExpenseStates
from app.finance.expense_service import process_expense

router = Router()


@router.message(F.text == "Внести трату")
async def start_expense_input(message: Message, state: FSMContext):
    await message.answer("Введите вашу трату. Например: потратил 500 рублей на ...")
    await state.set_state(ExpenseStates.waiting_for_expense_text)


@router.message(ExpenseStates.waiting_for_expense_text)
async def handle_expense_text(
    message: Message, state: FSMContext, user: User, session: AsyncSession
):
    try:
        expense = await process_expense(
            user_id=user.id,
            user_text=message.text,
            session=session,
        )
    except ValueError:
        await message.answer(
            "Не удалось распознать трату. Опишите подробнее, например: «потратил 500 в магните на чипсы»"
        )
        return

    await message.answer(
        f"Внесена трата суммой {expense.amount} в категорию {expense.category.name}"
    )
    await state.clear()
