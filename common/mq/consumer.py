from logging import getLogger
from typing import Callable

logger = getLogger(__name__)


class ConsumerGroup:
    all_workers = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.groups: list[ConsumerGroup] = []
        self._workers: dict[str, Callable] = {}

        logger.info(f"Initialized [{name}] group.")

    @property
    def workers(self) -> dict[str, Callable]:
        all_workers = self._workers.copy()
        for group in self.groups:
            all_workers |= group.workers
        return all_workers

    def get_full_name(self, name) -> str:
        return self.name + "." + name

    def group(self, name: str) -> "ConsumerGroup":
        full_name = self.get_full_name(name)
        _group = ConsumerGroup(full_name)
        self.groups.append(_group)
        logger.info(f"Added [{_group.name}] group to [{self.name}] group.")
        return _group

    def worker(self, name: str = None):
        def register(callback: Callable):
            if name:
                full_name = self.get_full_name(name)
            else:
                full_name = self.get_full_name(callback.__name__)

            async def wrapper(*args, **kwargs):
                logger.info(f"Executing [{full_name}] worker...")
                result = await callback(*args, **kwargs)
                logger.info(f"Done executing [{full_name}] worker.")
                return result

            self._workers[full_name] = wrapper
            ConsumerGroup.all_workers[full_name] = wrapper
            logger.info(f"Added [{full_name}] worker to [{self.name}] group.")

            return wrapper

        return register
