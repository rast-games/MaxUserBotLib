from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class FetchChatsMethod(BaseMaxApiMethod[list[Chat]]):
    async def __call__(self, marker: int | None = None) -> list[Chat]:
        if not self._max_api:
            raise RuntimeError("FetchChats method not bound to MaxApi instance")

        return cast(
            list[Chat],
            await self._max_api.mapper.call_method(
                type(self),
                marker=marker,
            ),
        )
