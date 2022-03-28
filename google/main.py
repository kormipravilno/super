from logging import getLogger

from common.logging import configure_logging
from google.config import config

configure_logging()
logger = getLogger(__name__)


if __name__ == "__main__":
    from google.loader import loop
    import google.consumer
    from common.mq import init_mq, close_mq

    loop.run_until_complete(init_mq(config.CLOUDAMQP_URL))

    try:
        logger.info("Consuming now.")
        loop.run_forever()
    finally:
        loop.run_until_complete(close_mq())
        loop.run_until_complete(loop.shutdown_asyncgens())
