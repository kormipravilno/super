from asyncio import get_event_loop

from aiogram import Bot, Dispatcher

from telegram.config import Config
from telegram.utils.redis_storage import RedisStorage3

loop = get_event_loop()
config = Config()

bot = Bot(config.TELEGRAM, parse_mode="HTML")

storage = RedisStorage3(
    config.REDISTOGO_URL.host,
    config.REDISTOGO_URL.port,
    password=config.REDISTOGO_URL.password,
)
dp = Dispatcher(bot, storage=storage)
