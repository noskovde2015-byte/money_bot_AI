from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Внести трату"), KeyboardButton(text="Внести доход")]
    ],
    resize_keyboard=True,
)
