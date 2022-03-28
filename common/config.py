from pydantic import BaseSettings, AmqpDsn


class BaseConfig(BaseSettings):
    CLOUDAMQP_URL: AmqpDsn

    class Config:
        env_file = "././.env"
