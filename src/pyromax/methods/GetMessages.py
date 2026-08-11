from typing import cast
from collections.abc import Iterable

from .Base import BaseMaxApiMethod
from ..models.Message import Message


class GetMessagesMethod(BaseMaxApiMethod[list[Message]]):
    async def __call__(
        self,
        chat_id: int,
        message_ids: Iterable[int | str],
    ) -> list[Message]:
        """Execute the get messages MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: Iterable[int | str]
        :returns: The resulting collection.
        :rtype: list[Message]
        :raises RuntimeError: If getMessages method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("GetMessages method not bound to MaxApi instance")

        return cast(
            list[Message],
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_ids=message_ids,
            ),
        )
