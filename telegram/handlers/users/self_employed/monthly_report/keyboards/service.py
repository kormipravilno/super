from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from common.schemas import SEServiceGet

from ..interfaces import MONTHLY_REPORT


service_callback = CallbackData(MONTHLY_REPORT.get_full_name("service"), "id")


def service_keyboard(services: list[SEServiceGet]):
    buttons = []
    for srv in services:
        buttons.append(
            [
                InlineKeyboardButton(
                    srv.name,
                    callback_data=service_callback.new(id=srv.id),
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                "▶️ Рассчитать ◀️",
                callback_data=service_callback.new(id=0),
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
