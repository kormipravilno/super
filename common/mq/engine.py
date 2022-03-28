from aio_pika import connect
from aio_pika.patterns import RPC
from logging import getLogger

from .consumer import ConsumerGroup

logger = getLogger(__name__)


async def init_mq(uri):
    logger.info("Initializing message queue...")
    global mq, channel, rpc
    mq = await connect(uri)
    channel = await mq.channel()
    rpc = await RPC.create(channel)
    for name, callback in ConsumerGroup.all_workers.items():
        await rpc.register(name, callback)
        logger.info(f"Registered [{name}] worker.")
    logger.info("Initialized message queue.")


async def close_mq():
    logger.info("Closing message queue...")
    await mq.close()
    logger.info("Closed message queue.")
