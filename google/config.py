from pydantic import AmqpDsn

from common.config import BaseConfig


class Config(BaseConfig):
    GOOGLE: dict
    CLOUDAMQP_URL: AmqpDsn


config = Config()
