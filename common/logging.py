import logging.config
import yaml


def configure_logging():
    with open("logging.yml", "r") as f:
        config = yaml.load(f, yaml.FullLoader)
    logging.config.dictConfig(config)
