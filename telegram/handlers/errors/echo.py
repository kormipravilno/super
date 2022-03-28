from aiogram.types import Update

from telegram.loader import dp


@dp.errors_handler()
async def echo_error(update: Update, error: BaseException):
    if update.message:
        message = update.message
    elif update.callback_query:
        message = update.callback_query.message
    text = (
        "Мне очень жаль, произошла непредвиденная ошибка 😔\n"
        "Пожалуйста, сообщи об этом разработчику..."
    )
    await message.answer(text)
