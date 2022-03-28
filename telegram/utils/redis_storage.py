import json
import typing

from aiogram.contrib.fsm_storage import redis as r
from aioredis.exceptions import ConnectionError


class RedisStorage3(r.RedisStorage2):
    """
    Fix disconnecting from idling too long
    """

    async def get_state(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[str] = None
    ) -> typing.Optional[str]:
        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, r.STATE_KEY)
        redis = await self._get_adapter()
        # there
        try:
            return await redis.get(key) or self.resolve_state(default)
        except ConnectionError:
            return await redis.get(key) or self.resolve_state(default)

    async def get_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[dict] = None
    ) -> typing.Dict:
        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, r.STATE_DATA_KEY)
        redis = await self._get_adapter()
        # and there
        try:
            raw_result = await redis.get(key)
        except ConnectionError:
            raw_result = await redis.get(key)
        if raw_result:
            return json.loads(raw_result)
        return default or {}
