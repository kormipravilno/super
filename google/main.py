from logging import getLogger

from common.logging import configure_logging

from google.config import config

configure_logging()
logger = getLogger(__name__)


if __name__ == "__main__":
    from common.mq import close_mq, init_mq

    import google.consumer
    from google.loader import loop

    loop.run_until_complete(init_mq(config.AMQP_URL))

    try:
        logger.info("Consuming now.")
        loop.run_forever()
    finally:
        loop.run_until_complete(close_mq())
        loop.run_until_complete(loop.shutdown_asyncgens())
