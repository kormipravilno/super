from aiogram.types import InlineKeyboardMarkup

from telegram.utils.dashboard import Dashboard


async def create_keyboard(id):
    handlers = await Dashboard.get_handlers(id)
    keyboard = []
    for handler in handlers:
        keyboard.append([handler.button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
