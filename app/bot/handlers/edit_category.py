from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.expense import Expense
from app.db.category import Category
from app.db.user import User

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
