from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    waiting_for_expense_text = State()


class IncomeStates(StatesGroup):
    waiting_for_income_amount = State()
