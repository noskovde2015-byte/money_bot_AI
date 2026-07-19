from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Внести трату"), KeyboardButton(text="Внести доход")],
        [KeyboardButton(text="Отчёт за месяц"), KeyboardButton(text="Годовой отчёт")],
    ],
    resize_keyboard=True,
)


def get_year_selection_keyboard(years: list[int]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=str(year), callback_data=f"yearly_report:{year}")]
        for year in years
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
