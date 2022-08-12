from pydantic import AmqpDsn, BaseSettings


class BaseConfig(BaseSettings):
    AMQP_URL: AmqpDsn

    class Config:
        env_file = "././.env"
