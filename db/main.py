import asyncio
from logging import getLogger

from common.logging import configure_logging

from db.config import config

configure_logging()
logger = getLogger(__name__)


from common.mq import close_mq, init_mq

from db.engine import close_db, init_db


async def init():
    import db.consumer

    await init_db()
    await init_mq(config.AMQP_URL)


async def close():
    await close_db()
    await close_mq()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(init())

    try:
        logger.info("Consuming now.")
        loop.run_forever()
    finally:
        loop.run_until_complete(close())
        loop.run_until_complete(loop.shutdown_asyncgens())
