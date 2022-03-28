from typing import Optional

from telegram.interfaces.base import InternalBase

from ...group import USERS


class HasStateStartInternal(InternalBase):
    key = USERS.name

    current_state: Optional[str]
