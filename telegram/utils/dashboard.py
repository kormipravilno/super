from logging import getLogger
from typing import Callable, Optional

from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from common.crud import CRUDBase
from telegram.loader import dp

logger = getLogger(__name__)


def get_full_name(self_name, name="", sep="/"):
    return self_name + sep + name


class Dashboard:
    def __init__(self, name: str, crud: CRUDBase = None) -> None:
        self.name = name
        self.crud = crud
        self.groups: list[Dashboard] = []
        self.handlers: list[DashboardHandler] = []

        logger.info(f"Initialized [{name}] group.")

    def get_full_name(self, name) -> str:
        return get_full_name(self.name, name)

    def group(self, name: str, crud: CRUDBase = None) -> "Dashboard":
        full_name = self.get_full_name(name)
        _group = Dashboard(full_name, crud)
        self.groups.append(_group)
        logger.info(f"Added [{_group.name}] group to [{self.name}] group.")
        return _group

    def handler(self, callback_name: str, button_text: str) -> "DashboardHandler":
        full_name = self.get_full_name(callback_name)
        handler = DashboardHandler(full_name, button_text)

        self.handlers.append(handler)
        logger.info(f"Added [{full_name}] handler to [{self.name}] group.")

        return handler

    async def __get_handlers(self, id: int) -> Optional[list["DashboardHandler"]]:
        if self.crud:
            obj = await self.crud.get(id)
            if obj:
                return self.handlers.copy()
            return None
        return self.handlers.copy()

    async def get_permitted_handlers(self, id: int) -> list["DashboardHandler"]:
        permitted_handlers = await self.__get_handlers(id)
        if permitted_handlers is not None:
            for group in self.groups:
                permitted_handlers.extend(await group.get_permitted_handlers(id))
            return permitted_handlers
        return []


class DashboardHandler:
    def __init__(self, name: str, button_text: str):
        self.callback_data = CallbackData(name)
        self.button = InlineKeyboardButton(button_text, callback_data=self.name)

    @property
    def name(self):
        return self.callback_data.new()

    def __call__(self, *custom_filters, state=None, run_task=None, **kwargs):
        def register(callback: Callable):
            dp.register_callback_query_handler(
                callback,
                self.callback_data.filter(),
                *custom_filters,
                state=state,
                run_task=run_task,
                **kwargs,
            )

            logger.info(f"Registered [{self.name}] handler.")

            return callback

        return register

    def get_full_name(self, name="") -> str:
        return get_full_name(self.name, name)
