from logging import getLogger
from aiogoogle import Aiogoogle

from google.loader import client, loop

logger = getLogger(__name__)


class Service:
    def __init_subclass__(cls, /, api_name=None, api_version=None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not (api_name and api_version):
            raise ValueError("api_name and api_version must be specified")
        cls.API = loop.run_until_complete(Service.discover(api_name, api_version))

    def __init__(self, client: Aiogoogle) -> None:
        self.client = client

    @staticmethod
    async def discover(name, version):
        logger.info(f"Discover {name} {version}")
        async with client as c:
            return await c.discover(name, version)
