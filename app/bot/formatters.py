from decimal import Decimal
from html import escape

from app.db.expense import Expense


def format_money(amount: Decimal | float) -> str:
    text = f"{amount:,.2f}".replace(",", " ")
    return f"{text.removesuffix('.00')}₽"


def format_expense_card(expense: Expense) -> str:
    lines = [
        f"💸 <b>{format_money(expense.amount)}</b> · {escape(expense.category.name)}"
    ]
    if expense.raw_text:
        lines.append(f"<i>«{escape(expense.raw_text)}»</i>")
    lines.append(f"📅 {expense.created_at:%d.%m.%Y}")
    if expense.is_harmful:
        lines.append("⚠️ Нежелательная трата")
    return "\n".join(lines)
