from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user import User
from app.bot.states import ExpenseStates
from app.finance.expense_service import process_expense
from app.bot.keyboards import get_edit_category_keyboard

router = Router()

BUTTON_TEXTS = {"Внести трату", "Внести доход", "Отчёт за месяц", "Годовой отчёт"}


@router.message(F.text == "Внести трату")
async def start_expense_input(message: Message, state: FSMContext):
    await message.answer(
        "Режим ввода трат включён. Пиши траты одну за другой, например: "
        "«потратил 500 рублей на такси». Чтобы выйти — нажми любую другую кнопку."
    )
    await state.set_state(ExpenseStates.waiting_for_expense_text)


@router.message(ExpenseStates.waiting_for_expense_text, F.text.not_in(BUTTON_TEXTS))
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
        f"Внесена трата суммой {expense.amount} в категорию {expense.category.name}",
        reply_markup=get_edit_category_keyboard(expense.id),
    )
