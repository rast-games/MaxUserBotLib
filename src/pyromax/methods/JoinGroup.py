from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class JoinGroupMethod(BaseMaxApiMethod[Chat]):
    async def __call__(self, link: str) -> Chat:
        """Execute the join group MAX API method.

        :param link: Invite, message, or resource link.
        :type link: str
        :returns: The resulting Chat value.
        :rtype: Chat
        :raises RuntimeError: If joinGroup method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("JoinGroup method not bound to MaxApi instance")

        return cast(
            Chat,
            await self._max_api.mapper.call_method(type(self), link=link),
        )


class JoinChannelMethod(BaseMaxApiMethod[Chat]):
    async def __call__(self, link: str) -> Chat:
        """Execute the join channel MAX API method.

        :param link: Invite, message, or resource link.
        :type link: str
        :returns: The resulting Chat value.
        :rtype: Chat
        :raises RuntimeError: If joinChannel method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("JoinChannel method not bound to MaxApi instance")

        return cast(
            Chat,
            await self._max_api.mapper.call_method(type(self), link=link),
        )
