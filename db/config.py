from common.config import BaseConfig
from pydantic import PostgresDsn


class Config(BaseConfig):
    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"


config = Config()
