from pydantic import BaseSettings, PostgresDsn, AmqpDsn


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
    CLOUDAMQP_URL: AmqpDsn

    class Config:
        env_file = ".env"


config = Config()
