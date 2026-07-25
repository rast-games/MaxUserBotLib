from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Member import Member


class GetJoinRequestsMethod(BaseMaxApiMethod[list[Member]]):
    async def __call__(self, chat_id: int, count: int = 100) -> list[Member]:
        if not self._max_api:
            raise RuntimeError("GetJoinRequests method not bound to MaxApi instance")

        return cast(
            list[Member],
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                count=count,
            ),
        )
