from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import MENU_BUTTONS, MenuButton
from app.bot.states import IncomeStates
from app.db.user import User
from app.finance.income_service import process_income

router = Router()


@router.message(F.text == MenuButton.ADD_INCOME)
async def start_income_input(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(IncomeStates.waiting_for_income_amount)
    await message.answer(
        "Режим ввода доходов включён. Пиши суммы одну за другой. "
        "Чтобы выйти — нажми любую другую кнопку."
    )


@router.message(
    IncomeStates.waiting_for_income_amount, F.text, F.text.not_in(MENU_BUTTONS)
)
async def handle_income_amount(message: Message, user: User, session: AsyncSession):
    try:
        income = await process_income(
            user_id=user.id, user_text=message.text, session=session
        )
    except ValueError:
        await message.answer(
            "Не удалось распознать доход. Попробуй написать точнее, например: "
            "«получил 30000 от Студии А» или просто «30000»"
        )
        return

    text = f"Записал доход: {income.amount}₽"
    if income.source:
        text += f" (источник: {income.source})"

    await message.answer(text)
