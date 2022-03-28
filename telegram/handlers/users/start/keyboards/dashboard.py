from pprint import pprint
from aiogram.types import InlineKeyboardMarkup

from telegram.handlers.users.group import USERS


async def handlers_keyboard(id):
    handlers = await USERS.get_permitted_handlers(id)
    keyboard = []
    for handler in handlers:
        keyboard.append([handler.button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
