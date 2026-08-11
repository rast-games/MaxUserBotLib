from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Message import Message


class LeaveGroupMethod(BaseMaxApiMethod[Union[Message, None]]):
    async def __call__(self, chat_id: int) -> Message | None:
        """Execute the leave group MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Message | None value.
        :rtype: Message | None
        :raises RuntimeError: If leaveGroup method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("LeaveGroup method not bound to MaxApi instance")

        return cast(
            Message | None,
            await self._max_api.mapper.call_method(type(self), chat_id=chat_id),
        )


class LeaveChannelMethod(BaseMaxApiMethod[Union[Message, None]]):
    async def __call__(self, chat_id: int) -> Message | None:
        """Execute the leave channel MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Message | None value.
        :rtype: Message | None
        :raises RuntimeError: If leaveChannel method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("LeaveChannel method not bound to MaxApi instance")

        return cast(
            Message | None,
            await self._max_api.mapper.call_method(type(self), chat_id=chat_id),
        )
