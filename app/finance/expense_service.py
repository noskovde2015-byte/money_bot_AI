from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.finance.category_service import find_similar_category
from app.core.llm.client import categorize_expense
from app.db.category import Category
from app.db.expense import Expense


async def process_expense(
    user_id: int, user_text: str, session: AsyncSession
) -> Expense:

    stmt = select(Category.name).where(Category.user_id == user_id)
    result = await session.execute(stmt)
    existing_categories = result.scalars().all()

    parsed = await categorize_expense(
        user_text=user_text, existing_categories=existing_categories
    )

    category = None

    if parsed.is_new_category is False:
        stmt_category = select(Category).where(
            Category.user_id == user_id,
            Category.name == parsed.category,
        )
        result = await session.execute(stmt_category)
        category = result.scalar_one_or_none()

    if category is None:
        sim = find_similar_category(
            new_name=parsed.category,
            existing_categories=existing_categories,
        )
        if sim is not None:
            stmt_similar = select(Category).where(
                Category.user_id == user_id,
                Category.name == sim,
            )
            result = await session.execute(stmt_similar)
            category = result.scalar_one_or_none()

    if category is None:
        category = Category(
            user_id=user_id,
            name=parsed.category,
            is_harmful=parsed.is_harmful,
            created_via_llm=True,
        )
        session.add(category)
        await session.flush()

    expense = Expense(
        user_id=user_id,
        category_id=category.id,
        amount=parsed.amount,
        raw_text=user_text,
        place=parsed.place,
        item=parsed.item,
        llm_confidence=parsed.confidence,
    )
    session.add(expense)

    await session.commit()
    await session.refresh(expense)

    return expense
