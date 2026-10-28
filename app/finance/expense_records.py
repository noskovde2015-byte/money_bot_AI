from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.category import Category
from app.db.expense import Expense
from app.finance.category_service import find_similar_category

MAX_AMOUNT = Decimal("99999999.99")  # предел колонки Numeric(10, 2)
MAX_CATEGORY_NAME_LENGTH = 40
RECENT_EXPENSES_LIMIT = 10


def parse_amount(raw: str) -> Decimal:
    normalized = (
        raw.strip()
        .removesuffix("₽")
        .replace(" ", "")
        .replace("\u00a0", "")
        .replace(",", ".")
    )
    try:
        amount = Decimal(normalized)
    except InvalidOperation:
        raise ValueError(
            "Не понял сумму. Напиши число, например 450 или 450,50"
        ) from None

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Сумма должна быть больше нуля.")
    if amount > MAX_AMOUNT:
        raise ValueError("Слишком большая сумма.")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def get_user_expense(
    session: AsyncSession, user_id: int, expense_id: int
) -> Expense | None:
    stmt = (
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.id == expense_id, Expense.user_id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_recent_expenses(
    session: AsyncSession, user_id: int, limit: int = RECENT_EXPENSES_LIMIT
) -> list[Expense]:
    stmt = (
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.user_id == user_id)
        .order_by(Expense.created_at.desc(), Expense.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_user_categories(session: AsyncSession, user_id: int) -> list[Category]:
    stmt = (
        select(Category)
        .where(Category.user_id == user_id)
        .order_by(Category.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_user_category(
    session: AsyncSession, user_id: int, category_id: int
) -> Category | None:
    stmt = select(Category).where(
        Category.id == category_id, Category.user_id == user_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_or_create_category(
    session: AsyncSession, user_id: int, raw_name: str
) -> Category:
    name = " ".join(raw_name.split())
    if not name:
        raise ValueError("Название категории не может быть пустым.")
    if len(name) > MAX_CATEGORY_NAME_LENGTH:
        raise ValueError(
            f"Слишком длинное название — максимум {MAX_CATEGORY_NAME_LENGTH} символов."
        )

    categories_by_name = {
        category.name: category
        for category in await get_user_categories(session, user_id)
    }
    similar = find_similar_category(
        new_name=name, existing_categories=list(categories_by_name)
    )
    if similar is not None:
        return categories_by_name[similar]

    category = Category(user_id=user_id, name=name, created_via_llm=False)
    session.add(category)
    await session.flush()
    return category


async def change_expense_category(
    session: AsyncSession, expense: Expense, category: Category
) -> None:
    expense.category = category
    await session.commit()


async def update_expense_amount(
    session: AsyncSession, expense: Expense, amount: Decimal
) -> None:
    expense.amount = amount
    await session.commit()


async def delete_expense(session: AsyncSession, expense: Expense) -> None:
    await session.delete(expense)
    await session.commit()
