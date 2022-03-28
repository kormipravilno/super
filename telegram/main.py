from aiogram import Dispatcher, executor

from common.mq import init_mq, close_mq
from common.logging import configure_logging
from db import init_db, close_db
from telegram.loader import dp, config, loop

configure_logging()


async def on_startup(dp: Dispatcher):
    await init_mq(config.CLOUDAMQP_URL)

    import telegram.middlewares
    import telegram.filters
    import telegram.handlers

    await init_db()


async def on_shutdown(dp: Dispatcher):
    await close_db()
    await close_mq()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
