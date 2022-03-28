from logging import getLogger
from typing import Callable, Optional, Type, TYPE_CHECKING
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import current_handler
from aiogram.types import Message, CallbackQuery

from telegram.loader import dp

from telegram.interfaces.base import InternalBase


logger = getLogger(__name__)


class InternalDataMiddleware(BaseMiddleware):
    @staticmethod
    def meta(InternalModel: InternalBase):
        return InternalModel.register()

    async def process(self, id: int, data: dict):
        handler = current_handler.get()
        InternalModel: Type[InternalBase] = getattr(handler, "internal_model", None)
        if InternalModel:
            storage_data = await dp.storage.get_data(user=id)
            internal_raw = storage_data.get(InternalModel.key)
            if internal_raw:
                internal = InternalModel.unpickle(internal_raw)
            else:
                internal = None
            logger.info(
                f"Passing {InternalModel.__name__} internal data to handler: {internal}"
            )
            data |= {"internal": internal, "internal_model": InternalModel}
        else:
            return

    async def on_process_message(self, message: Message, data: dict):
        await self.process(message.from_user.id, data)

    async def on_process_callback_query(self, call: CallbackQuery, data: dict):
        await self.process(call.from_user.id, data)

    async def post_process(self, id: int, data_from_handler: list[dict], data: dict):
        handler_internal = None
        if data_from_handler:
            handler_internal = data_from_handler[0].get("internal")
        data_internal = data.get("internal")
        internal: Optional[InternalBase] = handler_internal or data_internal

        if internal:
            InternalModel: InternalBase = data.get("internal_model")
            if InternalModel:
                # .copy() exludes fields.
                # TODO: check if there are values to exclude.
                internal = internal.copy()
                logger.info(
                    f"Updating {InternalModel.__name__} internal data from handler: {internal}"
                )
                internal_data = {InternalModel.key: internal.pickle()}
                await dp.storage.update_data(user=id, data=internal_data)

    async def on_post_process_message(
        self, message: Message, data_from_handler: list[dict], data: dict
    ):
        id = message.from_user.id
        await self.post_process(id, data_from_handler, data)

    async def on_post_process_callback_query(
        self, call: CallbackQuery, data_from_handler: list[dict], data: dict
    ):
        id = call.from_user.id
        await self.post_process(id, data_from_handler, data)


dp.middleware.setup(InternalDataMiddleware())
