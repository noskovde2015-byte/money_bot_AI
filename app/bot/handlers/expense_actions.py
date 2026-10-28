from contextlib import suppress
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callbacks import ExpenseAction, ExpenseCallback
from app.bot.formatters import format_expense_card, format_money
from app.bot.keyboards import (
    MENU_BUTTONS,
    MenuButton,
    back_to_expense_keyboard,
    category_choice_keyboard,
    delete_confirm_keyboard,
    expense_card_keyboard,
    recent_expenses_keyboard,
    recent_list_keyboard,
)
from app.bot.states import ExpenseEditStates
from app.db.expense import Expense
from app.db.user import User
from app.finance.expense_records import (
    change_expense_category,
    delete_expense,
    get_or_create_category,
    get_recent_expenses,
    get_user_categories,
    get_user_category,
    get_user_expense,
    parse_amount,
    update_expense_amount,
)

router = Router()

RECENT_HEADER = "📋 <b>Последние траты</b>\nВыбери запись, чтобы изменить или удалить:"
EMPTY_RECENT = "Трат пока нет — начни с кнопки «Внести трату»."
EXPENSE_NOT_FOUND = "Запись не найдена — возможно, она уже удалена."
LEGACY_CALLBACK_PREFIXES = ("edit_category:", "set_category:", "new_category:")

_EDIT_STATES = frozenset(
    {
        ExpenseEditStates.waiting_for_amount.state,
        ExpenseEditStates.waiting_for_category_name.state,
    }
)


async def _render(
    callback: CallbackQuery, text: str, markup: InlineKeyboardMarkup | None = None
) -> None:
    """Перерисовывает сообщение с кнопками и снимает «часики» с нажатой кнопки."""
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer(
            "Сообщение устарело — открой «Последние траты».", show_alert=True
        )
        return
    try:
        await message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise
    await callback.answer()


async def _get_expense_or_alert(
    callback: CallbackQuery, session: AsyncSession, user: User, expense_id: int
) -> Expense | None:
    expense = await get_user_expense(session, user_id=user.id, expense_id=expense_id)
    if expense is None:
        await callback.answer(EXPENSE_NOT_FOUND, show_alert=True)
    return expense


async def _start_edit(state: FSMContext, edit_state: State, expense_id: int) -> None:
    """Входит в режим редактирования, запоминая режим, в который нужно вернуться."""
    current_state = await state.get_state()
    if current_state in _EDIT_STATES:
        return_state = (await state.get_data()).get("return_state")
    else:
        return_state = current_state

    await state.set_state(edit_state)
    await state.set_data({"expense_id": expense_id, "return_state": return_state})


async def _finish_edit(state: FSMContext) -> None:
    """Выходит из редактирования и возвращает пользователя в прежний режим ввода."""
    data = await state.get_data()
    await state.set_data({})
    await state.set_state(data.get("return_state"))


async def _leave_edit_if_active(state: FSMContext) -> None:
    if await state.get_state() in _EDIT_STATES:
        await _finish_edit(state)


@router.message(F.text == MenuButton.RECENT_EXPENSES)
async def show_recent_expenses(
    message: Message, state: FSMContext, user: User, session: AsyncSession
):
    await _leave_edit_if_active(state)

    expenses = await get_recent_expenses(session, user_id=user.id)
    if not expenses:
        await message.answer(EMPTY_RECENT)
        return

    await message.answer(
        RECENT_HEADER,
        reply_markup=recent_expenses_keyboard(expenses),
        parse_mode="HTML",
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.LIST))
async def back_to_recent_list(
    callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession
):
    await _leave_edit_if_active(state)

    expenses = await get_recent_expenses(session, user_id=user.id)
    if not expenses:
        await _render(callback, EMPTY_RECENT)
        return

    await _render(callback, RECENT_HEADER, recent_expenses_keyboard(expenses))


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.CLOSE))
async def close_recent_list(callback: CallbackQuery, state: FSMContext):
    await _leave_edit_if_active(state)

    message = callback.message
    if isinstance(message, Message):
        try:
            await message.delete()
        except TelegramBadRequest:
            # Telegram не даёт удалять сообщения старше 48 часов — тогда просто убираем кнопки
            with suppress(TelegramBadRequest):
                await message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.OPEN))
async def open_expense(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    await _leave_edit_if_active(state)

    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    await _render(callback, format_expense_card(expense), expense_card_keyboard(expense.id))


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.EDIT_CATEGORY))
async def choose_category(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    categories = await get_user_categories(session, user_id=user.id)
    await _render(
        callback,
        f"Выбери категорию для траты <b>{format_money(expense.amount)}</b>:",
        category_choice_keyboard(expense.id, categories, expense.category_id),
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.SET_CATEGORY))
async def set_category(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    category = await get_user_category(
        session, user_id=user.id, category_id=callback_data.category_id
    )
    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    if category.id != expense.category_id:
        await change_expense_category(session, expense, category)

    await _render(
        callback,
        f"✅ Категория изменена\n\n{format_expense_card(expense)}",
        expense_card_keyboard(expense.id),
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.NEW_CATEGORY))
async def ask_category_name(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    await _start_edit(state, ExpenseEditStates.waiting_for_category_name, expense.id)
    await _render(
        callback,
        "Напиши название категории для этой траты:",
        back_to_expense_keyboard(expense.id),
    )


@router.message(
    ExpenseEditStates.waiting_for_category_name, F.text, F.text.not_in(MENU_BUTTONS)
)
async def receive_category_name(
    message: Message, state: FSMContext, user: User, session: AsyncSession
):
    data = await state.get_data()
    expense = await get_user_expense(
        session, user_id=user.id, expense_id=data.get("expense_id", 0)
    )
    if expense is None:
        await _finish_edit(state)
        await message.answer(EXPENSE_NOT_FOUND)
        return

    try:
        category = await get_or_create_category(
            session, user_id=user.id, raw_name=message.text
        )
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await change_expense_category(session, expense, category)
    await _finish_edit(state)
    await message.answer(
        f"✅ Категория изменена\n\n{format_expense_card(expense)}",
        reply_markup=expense_card_keyboard(expense.id),
        parse_mode="HTML",
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.EDIT_AMOUNT))
async def ask_new_amount(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    await _start_edit(state, ExpenseEditStates.waiting_for_amount, expense.id)
    await _render(
        callback,
        f"Сейчас: <b>{format_money(expense.amount)}</b>\n"
        "Напиши новую сумму, например <code>450</code> или <code>450,50</code>:",
        back_to_expense_keyboard(expense.id),
    )


@router.message(
    ExpenseEditStates.waiting_for_amount, F.text, F.text.not_in(MENU_BUTTONS)
)
async def receive_new_amount(
    message: Message, state: FSMContext, user: User, session: AsyncSession
):
    try:
        amount = parse_amount(message.text)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    data = await state.get_data()
    expense = await get_user_expense(
        session, user_id=user.id, expense_id=data.get("expense_id", 0)
    )
    await _finish_edit(state)
    if expense is None:
        await message.answer(EXPENSE_NOT_FOUND)
        return

    await update_expense_amount(session, expense, amount)
    await message.answer(
        f"✅ Сумма изменена\n\n{format_expense_card(expense)}",
        reply_markup=expense_card_keyboard(expense.id),
        parse_mode="HTML",
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.DELETE))
async def ask_delete_confirmation(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    await _render(
        callback,
        f"Удалить эту трату?\n\n{format_expense_card(expense)}",
        delete_confirm_keyboard(expense.id),
    )


@router.callback_query(ExpenseCallback.filter(F.action == ExpenseAction.DELETE_CONFIRM))
async def confirm_delete(
    callback: CallbackQuery,
    callback_data: ExpenseCallback,
    user: User,
    session: AsyncSession,
):
    expense = await _get_expense_or_alert(callback, session, user, callback_data.expense_id)
    if expense is None:
        return

    summary = f"{format_money(expense.amount)} · {escape(expense.category.name)}"
    await delete_expense(session, expense)
    await _render(callback, f"🗑 Трата удалена: {summary}", recent_list_keyboard())


@router.callback_query(F.data.startswith(LEGACY_CALLBACK_PREFIXES))
async def legacy_buttons(callback: CallbackQuery):
    """Кнопки старого формата под сообщениями, отправленными до обновления."""
    await callback.answer(
        "Эта кнопка устарела — открой «Последние траты» в меню.", show_alert=True
    )
