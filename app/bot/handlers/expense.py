from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.formatters import format_expense_card
from app.bot.keyboards import MENU_BUTTONS, MenuButton, expense_card_keyboard
from app.bot.states import ExpenseStates
from app.db.user import User
from app.finance.expense_service import process_expense

router = Router()


@router.message(F.text == MenuButton.ADD_EXPENSE)
async def start_expense_input(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ExpenseStates.waiting_for_expense_text)
    await message.answer(
        "Режим ввода трат включён. Пиши траты одну за другой, например: "
        "«потратил 500 рублей на такси». Чтобы выйти — нажми любую другую кнопку."
    )


@router.message(
    ExpenseStates.waiting_for_expense_text, F.text, F.text.not_in(MENU_BUTTONS)
)
async def handle_expense_text(message: Message, user: User, session: AsyncSession):
    try:
        expense = await process_expense(
            user_id=user.id,
            user_text=message.text,
            session=session,
        )
    except ValueError:
        await message.answer(
            "Не удалось распознать трату. Опиши подробнее, например: "
            "«потратил 500 в магните на чипсы»"
        )
        return

    await message.answer(
        f"✅ Записал\n\n{format_expense_card(expense)}",
        reply_markup=expense_card_keyboard(expense.id),
        parse_mode="HTML",
    )
