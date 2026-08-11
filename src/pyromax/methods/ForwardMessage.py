from typing import cast, Optional

from .Base import BaseMaxApiMethod
from ..models.Message import Message


class ForwardMessageMethod(BaseMaxApiMethod[Optional[Message]]):
    async def __call__(
        self,
        message_id: int | str,
        from_chat_id: int,
        to_chat_id: int,
        notify: bool = True,
    ) -> Message | None:
        """Execute the forward message MAX API method.

        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param from_chat_id: Identifier of the source chat.
        :type from_chat_id: int
        :param to_chat_id: Identifier of the destination chat.
        :type to_chat_id: int
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :returns: The resulting Message | None value.
        :rtype: Message | None
        :raises RuntimeError: If forwardMessage method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ForwardMessage method not bound to MaxApi instance")
        return cast(
            Message | None,
            await self._max_api.mapper.call_method(
                type(self),
                message_id=message_id,
                from_chat_id=from_chat_id,
                to_chat_id=to_chat_id,
                notify=notify,
            ),
        )
