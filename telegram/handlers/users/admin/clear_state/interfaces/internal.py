from typing import ClassVar, Optional

from telegram.interfaces.base import InternalBase

from ...group import ADMIN


CLEAR_STATE = ADMIN.handler("clear_state", "Обнулить состояние пользователя")


# TODO: utilize Service model
class ClearStateInternal(InternalBase):
    key: ClassVar = CLEAR_STATE.name

    current_state: Optional[str]

    class Config:
        arbitrary_types_allowed = True
