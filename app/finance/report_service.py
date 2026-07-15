from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.expense import Expense
from app.db.category import Category
from app.db.income import Income


async def get_total_expenses(
    user_id: int, start_date: datetime, end_date: datetime, session: AsyncSession
) -> Decimal:
    stmt = select(func.sum(Expense.amount)).where(
        Expense.user_id == user_id,
        Expense.created_at >= start_date,
        Expense.created_at < end_date,
    )
    result = await session.execute(stmt)
    total = result.scalar_one_or_none()

    return total if total is not None else Decimal("0")


async def get_expenses_by_category(
    user_id: int, start_date: datetime, end_date: datetime, session: AsyncSession
) -> list[tuple[str, Decimal]]:
    stmt = (
        select(Category.name, func.sum(Expense.amount))
        .join(Category, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user_id,
            Expense.created_at >= start_date,
            Expense.created_at < end_date,
        )
        .group_by(Category.name)
    )
    result = await session.execute(stmt)
    return result.all()


async def get_harmful_expenses_total(
    user_id: int, start_date: datetime, end_date: datetime, session: AsyncSession
) -> Decimal:
    stmt = select(func.sum(Expense.amount)).where(
        Expense.user_id == user_id,
        Expense.created_at >= start_date,
        Expense.created_at < end_date,
        Expense.is_harmful == True,
    )
    result = await session.execute(stmt)
    total = result.scalar_one_or_none()
    return total if total is not None else Decimal("0")


async def get_total_incomes(
    user_id: int, start_date: datetime, end_date: datetime, session: AsyncSession
) -> Decimal:
    stmt = select(func.sum(Income.amount)).where(
        Income.user_id == user_id,
        Income.created_at >= start_date,
        Income.created_at < end_date,
    )
    result = await session.execute(stmt)
    total = result.scalar_one_or_none()
    return total if total is not None else Decimal("0")


def get_month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    return start_date, end_date


async def build_monthly_report(user_id: int, session: AsyncSession) -> dict:
    today = datetime.now()

    current_start, current_end = get_month_bounds(today.year, today.month)

    if today.month == 1:
        prev_start, prev_end = get_month_bounds(today.year - 1, 12)
    else:
        prev_start, prev_end = get_month_bounds(today.year, today.month - 1)

    current_expenses = await get_total_expenses(
        user_id, current_start, current_end, session
    )
    current_incomes = await get_total_incomes(
        user_id, current_start, current_end, session
    )
    by_category = await get_expenses_by_category(
        user_id, current_start, current_end, session
    )
    harmful_total = await get_harmful_expenses_total(
        user_id, current_start, current_end, session
    )
    prev_expenses = await get_total_expenses(user_id, prev_start, prev_end, session)

    if prev_expenses > 0:
        change_percent = float((current_expenses - prev_expenses) / prev_expenses * 100)
    else:
        change_percent = None

    return {
        "current_expenses": current_expenses,
        "current_incomes": current_incomes,
        "by_category": by_category,
        "harmful_total": harmful_total,
        "prev_expenses": prev_expenses,
        "change_percent": change_percent,
    }


if __name__ == "__main__":
    import asyncio
    from app.db.db_helper import db_helper

    async def test():
        async with db_helper.session_factory() as session:
            report = await build_monthly_report(user_id=1, session=session)
            print(report)

    asyncio.run(test())
