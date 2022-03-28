from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from ..interfaces import DAILY_REPORT

proceed_final_callback = CallbackData(DAILY_REPORT.get_full_name("proceed_final"))

proceed_final_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                "Закрыть отчет", callback_data=proceed_final_callback.new()
            )
        ]
    ]
)
