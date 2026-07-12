from sqlalchemy.ext.asyncio import AsyncSession

from app.db.income import Income


async def process_income(user_id: int, raw_text: str, session: AsyncSession) -> Income:
    try:
        amount = float(raw_text)
    except ValueError:
        raise ValueError("Некорректный формат записи дохода")

    income = Income(user_id=user_id, amount=amount)
    session.add(income)
    await session.commit()
    await session.refresh(income)
    return income
