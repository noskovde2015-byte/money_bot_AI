from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.expense import Expense
from app.db.category import Category
from app.db.user import User
from app.bot.states import EditCategoryStates
from app.finance.category_service import find_similar_category

router = Router()


@router.callback_query(F.data.startswith("edit_category:"))
async def show_category_choices(
    callback: CallbackQuery, user: User, session: AsyncSession
):
    expense_id = int(callback.data.split(":")[1])

    stmt = select(Category).where(Category.user_id == user.id)
    result = await session.execute(stmt)
    categories = result.scalars().all()

    buttons = [
        [
            InlineKeyboardButton(
                text=cat.name, callback_data=f"set_category:{expense_id}:{cat.id}"
            )
        ]
        for cat in categories
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Другая категория", callback_data=f"new_category:{expense_id}"
            )
        ]
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "Выбери правильную категорию:",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_category:"))
async def apply_new_category(callback: CallbackQuery, session: AsyncSession):
    _, expense_id, category_id = callback.data.split(":")
    expense_id, category_id = int(expense_id), int(category_id)

    expense_stmt = select(Expense).where(Expense.id == expense_id)
    expense_result = await session.execute(expense_stmt)
    expense = expense_result.scalar_one_or_none()

    category_stmt = select(Category).where(Category.id == category_id)
    category_result = await session.execute(category_stmt)
    category = category_result.scalar_one_or_none()

    if expense is None or category is None:
        await callback.answer("Что-то пошло не так", show_alert=True)
        return

    expense.category_id = category.id
    await session.commit()

    await callback.message.edit_text(
        f"Готово! Трата суммой {expense.amount} теперь в категории «{category.name}»"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("new_category:"))
async def ask_new_category(callback: CallbackQuery, state: FSMContext):
    expense_id = int(callback.data.split(":")[1])

    await state.update_data(expense_id=expense_id)
    await state.set_state(EditCategoryStates.waiting_for_new_category)

    await callback.message.edit_text("Напиши название новой категории:")
    await callback.answer()


@router.message(EditCategoryStates.waiting_for_new_category)
async def apply_custom_category(
    message: Message, state: FSMContext, user: User, session: AsyncSession
):
    data = await state.get_data()
    expense_id = data["expense_id"]

    new_category_name = message.text

    stmt = select(Category.name).where(Category.user_id == user.id)
    result = await session.execute(stmt)
    existing_categories = result.scalars().all()

    similar = find_similar_category(
        new_name=new_category_name, existing_categories=existing_categories
    )
    category_name = similar if similar is not None else new_category_name

    category_stmt = select(Category).where(
        Category.user_id == user.id, Category.name == category_name
    )
    category_result = await session.execute(category_stmt)
    category = category_result.scalar_one_or_none()

    if category is None:
        category = Category(user_id=user.id, name=category_name, created_via_llm=False)
        session.add(category)
        await session.flush()

    expense_stmt = select(Expense).where(Expense.id == expense_id)
    expense_result = await session.execute(expense_stmt)
    expense = expense_result.scalar_one_or_none()

    expense.category_id = category.id
    await session.commit()

    await message.answer(f"Готово! Трата теперь в категории «{category.name}»")
    await state.clear()
