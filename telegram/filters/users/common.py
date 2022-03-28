from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter

from common.crud import CRUDBase


class UserFilter(BoundFilter):
    def __init_subclass__(cls, /, crud: CRUDBase, **kwargs) -> None:
        cls.crud = crud
        super().__init_subclass__(**kwargs)

    async def check(self, message: Message) -> bool:
        user = await self.crud.get(message.from_user.id)
        if user:
            return {self.crud.model.__tablename__: user}
