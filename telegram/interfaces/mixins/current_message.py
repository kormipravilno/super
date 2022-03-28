from typing import Optional
import aiogram.types
from pydantic import BaseModel

from telegram.loader import dp


class Message(BaseModel):
    id: int
    chat_id: int

    async def delete(self):
        await dp.bot.delete_message(self.chat_id, self.id)


class CurrentMessageMixin(BaseModel):
    current_message: Optional[Message] = None

    def set_current_message(self, value):
        if isinstance(value, aiogram.types.Message):
            self.current_message = Message(
                id=value.message_id,
                chat_id=value.chat.id,
            )
        elif value is None:
            self.current_message = None
        else:
            raise ValueError("value must be either aiogram.types.Message or None")
