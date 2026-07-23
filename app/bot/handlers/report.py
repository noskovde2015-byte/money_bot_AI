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
    insight = insight.replace("$", "")

    category_lines = (
        "\n".join(f"  • {name}: {total}₽" for name, total in report_data["by_category"])
        or "  нет данных"
    )

    source_lines = "\n".join(
        f"  • {name}: {total}₽" for name, total in report_data["by_source"]
    )

    if report_data["change_percent"] is not None:
        change_line = (
            f"📈 Изменение к прошлому месяцу: {report_data['change_percent']:+.1f}%"
        )
    else:
        change_line = "📈 Нет данных за прошлый месяц для сравнения"

    balance = report_data["current_incomes"] - report_data["current_expenses"]

    parts = [
        f"📊 <b>Отчёт за {report_data['month_name']}</b>",
        "",
        f"💰 <b>Доходы:</b> {report_data['current_incomes']}₽",
    ]

    if source_lines:
        parts.append(f"<b>По источникам:</b>\n{source_lines}")

    parts += [
        "",
        f"💸 <b>Траты:</b> {report_data['current_expenses']}₽",
        f"<b>По категориям:</b>\n{category_lines}",
        "",
        f"⚖️ <b>Дельта:</b> {balance}₽",
        "",
        f"⚠️ Нежелательные траты: {report_data['harmful_total']}₽",
        change_line,
        "",
        f"💡 {insight}",
    ]

    text = "\n".join(parts)
    await message.answer(text, parse_mode="HTML")
