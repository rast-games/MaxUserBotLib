from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Member import Member


class GetJoinRequestsMethod(BaseMaxApiMethod[list[Member]]):
    async def __call__(self, chat_id: int, count: int = 100) -> list[Member]:
        """Execute the get join requests MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param count: Maximum number of items to retrieve.
        :type count: int
        :returns: The resulting collection.
        :rtype: list[Member]
        :raises RuntimeError: If getJoinRequests method not bound to MaxApi instance.
        """
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
