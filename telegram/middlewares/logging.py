from aiogram.contrib.middlewares.logging import LoggingMiddleware

from telegram.loader import dp

dp.middleware.setup(LoggingMiddleware())
