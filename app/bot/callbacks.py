from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class ExpenseAction(StrEnum):
    OPEN = "open"
    LIST = "list"
    EDIT_CATEGORY = "cat"
    SET_CATEGORY = "setcat"
    NEW_CATEGORY = "newcat"
    EDIT_AMOUNT = "amount"
    DELETE = "del"
    DELETE_CONFIRM = "delok"


class ExpenseCallback(CallbackData, prefix="exp"):
    action: ExpenseAction
    expense_id: int = 0
    category_id: int = 0
