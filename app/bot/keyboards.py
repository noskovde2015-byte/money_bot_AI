from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Внести трату"), KeyboardButton(text="Внести доход")],
        [KeyboardButton(text="Отчёт за месяц")],
    ],
    resize_keyboard=True,
)
