from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    waiting_for_expense_text = State()


class IncomeStates(StatesGroup):
    waiting_for_income_amount = State()


class ExpenseEditStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category_name = State()
