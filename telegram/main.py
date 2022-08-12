from aiogram import Dispatcher, executor
from common.logging import configure_logging
from common.mq import close_mq, init_mq
from db import close_db, init_db

from telegram.loader import config, dp, loop

configure_logging()


async def on_startup(dp: Dispatcher):
    await init_mq(config.AMQP_URL)

    import telegram.filters
    import telegram.handlers
    import telegram.middlewares

    await init_db()


async def on_shutdown(dp: Dispatcher):
    await close_db()
    await close_mq()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
