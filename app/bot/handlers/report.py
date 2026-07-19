from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user import User
from app.finance.report_service import build_monthly_report
from app.core.llm.client import generate_report_insight

router = Router()


@router.message(F.text == "Отчёт за месяц")
async def handle_monthly_report(message: Message, user: User, session: AsyncSession):
    report_data = await build_monthly_report(user_id=user.id, session=session)
    insight = await generate_report_insight(report_data=report_data)

    category_lines = "\n".join(
        f"  • {name}: {total}₽" for name, total in report_data["by_category"]
    )

    if report_data["change_percent"] is not None:
        change_line = (
            f"\n📈 Изменение к прошлому месяцу: {report_data['change_percent']:+.1f}%"
        )
    else:
        change_line = "\n📈 Нет данных за прошлый месяц для сравнения"

    balance = report_data["current_incomes"] - report_data["current_expenses"]

    text = (
        f"📊 <b>Отчёт за {report_data['month_name']}</b>\n\n"
        f"💰 Доходы: {report_data['current_incomes']}₽\n"
        f"💸 Траты: {report_data['current_expenses']}₽\n"
        f"⚖️ Дельта: {balance}₽\n\n"
        f"<b>По категориям:</b>\n{category_lines}\n\n"
        f"⚠️ Нежелательные траты: {report_data['harmful_total']}₽"
        f"{change_line}\n\n"
        f"💡 {insight}"
    )

    await message.answer(text, parse_mode="HTML")
