from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class Buttons:
    yes = KeyboardButton("Да")
    no = KeyboardButton("Нет")
    none = KeyboardButton("Не было")
    ready = KeyboardButton("Готово")
    okay = KeyboardButton("✅ Да, все верно!")
    not_okay = KeyboardButton("↩️ Мне нужно что-то изменить...")
    proceed = KeyboardButton("Продолжить")


yes_no = ReplyKeyboardMarkup(
    keyboard=[[Buttons.yes, Buttons.no]],
    resize_keyboard=True,
)

yes = ReplyKeyboardMarkup(
    keyboard=[[Buttons.yes]],
    resize_keyboard=True,
)

none = ReplyKeyboardMarkup(
    keyboard=[[Buttons.none]],
    resize_keyboard=True,
)

ready = ReplyKeyboardMarkup(
    keyboard=[[Buttons.ready]],
    resize_keyboard=True,
)

is_okay = ReplyKeyboardMarkup(
    keyboard=[[Buttons.okay], [Buttons.not_okay]],
    resize_keyboard=True,
)
