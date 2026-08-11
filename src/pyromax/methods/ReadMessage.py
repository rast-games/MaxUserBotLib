from typing import cast

from .Base import BaseMaxApiMethod
from ..models.ReadState import ReadState


class ReadMessageMethod(BaseMaxApiMethod[ReadState]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        mark: int,
        typeof: str = "READ_MESSAGE",
    ) -> ReadState:
        """Execute the read message MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param mark: The mark value.
        :type mark: int
        :param typeof: Attachment class that determines the upload type.
        :type typeof: str
        :returns: The resulting ReadState value.
        :rtype: ReadState
        :raises RuntimeError: If readMessage method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ReadMessage method not bound to MaxApi instance")
        return cast(
            ReadState,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                mark=mark,
                typeof=typeof,
            ),
        )
