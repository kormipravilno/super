from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message
from telegram.loader import config, dp

from .interfaces import UPDATE_SETTINGS
from .producers import update


@dp.message_handler(commands=[f"update_db_{config.DB_UPDATE_PASSWORD}"])
async def update_settings_msg(message: Message):
    await message.delete()
    await message.answer("Обновление базы данных...")
    await update()
    await message.answer("Обновление базы данных завершено.")


@UPDATE_SETTINGS()
async def update_settings(call: CallbackQuery):
    await call.message.edit_text("🤔 Загружаю данные...")
    await update()

    await call.message.delete()
    await call.message.answer("Настройки успешно обновлены")
