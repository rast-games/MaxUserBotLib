from typing import cast
from collections.abc import Iterable

from .Base import BaseMaxApiMethod
from ..models import Chat


class GetChatsMethod(BaseMaxApiMethod[list[Chat]]):
    async def __call__(self, chat_ids: Iterable[int]) -> list[Chat]:
        if not self._max_api:
            raise RuntimeError("GetChats method not bound to MaxApi instance")

        return cast(
            list[Chat],
            await self._max_api.mapper.call_method(
                type(self),
                chat_ids=chat_ids,
            ),
        )
