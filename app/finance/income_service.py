from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm.client import categorize_income
from app.db.income import Income
from app.finance.category_service import find_similar_category


async def process_income(user_id: int, user_text: str, session: AsyncSession) -> Income:
    stmt = (
        select(Income.source)
        .where(Income.user_id == user_id, Income.source.is_not(None))
        .distinct()
    )
    result = await session.execute(stmt)
    existing_sources = result.scalars().all()

    parsed = await categorize_income(
        user_text=user_text, existing_sources=existing_sources
    )

    if parsed.amount is None:
        raise ValueError("Не удалось распознать доход")

    source = parsed.source
    if source is not None:
        similar = find_similar_category(
            new_name=source, existing_categories=existing_sources
        )
        if similar is not None:
            source = similar

    income = Income(user_id=user_id, amount=parsed.amount, source=source)
    session.add(income)
    await session.commit()
    await session.refresh(income)
    return income
