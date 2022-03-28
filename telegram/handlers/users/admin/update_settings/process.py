from aiogram.types import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from .interfaces import UPDATE_SETTINGS
from .producers import update


@UPDATE_SETTINGS()
async def update_settings(call: CallbackQuery):
    await call.message.edit_text("🤔 Загружаю данные...")
    await update()

    await call.message.delete()
    await call.message.answer("Настройки успешно обновлены")
