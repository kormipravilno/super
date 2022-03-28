import asyncio
from logging import getLogger

from common.logging import configure_logging
from db.config import config

configure_logging()
logger = getLogger(__name__)


async def main():
    from common.mq import init_mq, close_mq

    await init_mq(config.CLOUDAMQP_URL)

    from common.mq.engine import rpc

    await rpc.call("db.update")

    await close_mq()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())

    loop.close()
