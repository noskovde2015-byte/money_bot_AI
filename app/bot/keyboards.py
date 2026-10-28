from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.bot.callbacks import ExpenseAction, ExpenseCallback
from app.bot.formatters import format_money
from app.db.category import Category
from app.db.expense import Expense

BUTTON_TEXT_LIMIT = 60


class MenuButton:
    ADD_EXPENSE = "Внести трату"
    ADD_INCOME = "Внести доход"
    MONTHLY_REPORT = "Отчёт за месяц"
    YEARLY_REPORT = "Годовой отчёт"
    RECENT_EXPENSES = "Последние траты"


MENU_BUTTONS = frozenset(
    {
        MenuButton.ADD_EXPENSE,
        MenuButton.ADD_INCOME,
        MenuButton.MONTHLY_REPORT,
        MenuButton.YEARLY_REPORT,
        MenuButton.RECENT_EXPENSES,
    }
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=MenuButton.ADD_EXPENSE),
            KeyboardButton(text=MenuButton.ADD_INCOME),
        ],
        [
            KeyboardButton(text=MenuButton.MONTHLY_REPORT),
            KeyboardButton(text=MenuButton.YEARLY_REPORT),
        ],
        [KeyboardButton(text=MenuButton.RECENT_EXPENSES)],
    ],
    resize_keyboard=True,
)


def get_year_selection_keyboard(years: list[int]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=str(year), callback_data=f"yearly_report:{year}")]
        for year in years
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _shorten(text: str) -> str:
    if len(text) <= BUTTON_TEXT_LIMIT:
        return text
    return text[: BUTTON_TEXT_LIMIT - 1] + "…"


def _expense_button(
    text: str, action: ExpenseAction, expense_id: int = 0, category_id: int = 0
) -> InlineKeyboardButton:
    callback_data = ExpenseCallback(
        action=action, expense_id=expense_id, category_id=category_id
    )
    return InlineKeyboardButton(text=text, callback_data=callback_data.pack())


def expense_card_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _expense_button("✏️ Категория", ExpenseAction.EDIT_CATEGORY, expense_id),
                _expense_button("💰 Сумма", ExpenseAction.EDIT_AMOUNT, expense_id),
            ],
            [_expense_button("🗑 Удалить", ExpenseAction.DELETE, expense_id)],
            [_expense_button("📋 Последние траты", ExpenseAction.LIST)],
        ]
    )


def delete_confirm_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _expense_button("✅ Да, удалить", ExpenseAction.DELETE_CONFIRM, expense_id),
                _expense_button("↩️ Отмена", ExpenseAction.OPEN, expense_id),
            ]
        ]
    )


def back_to_expense_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[_expense_button("↩️ Отмена", ExpenseAction.OPEN, expense_id)]]
    )


def recent_list_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[_expense_button("📋 Последние траты", ExpenseAction.LIST)]]
    )


def category_choice_keyboard(
    expense_id: int, categories: list[Category], current_category_id: int
) -> InlineKeyboardMarkup:
    buttons = [
        _expense_button(
            _shorten(("✅ " if category.id == current_category_id else "") + category.name),
            ExpenseAction.SET_CATEGORY,
            expense_id,
            category.id,
        )
        for category in categories
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append(
        [_expense_button("➕ Новая категория", ExpenseAction.NEW_CATEGORY, expense_id)]
    )
    rows.append([_expense_button("↩️ Назад", ExpenseAction.OPEN, expense_id)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def recent_expenses_keyboard(expenses: list[Expense]) -> InlineKeyboardMarkup:
    rows = [
        [
            _expense_button(
                _shorten(
                    f"{format_money(expense.amount)} · {expense.category.name} · "
                    f"{expense.created_at:%d.%m}"
                ),
                ExpenseAction.OPEN,
                expense.id,
            )
        ]
        for expense in expenses
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
