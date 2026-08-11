from typing import cast
from .Base import BaseMaxApiMethod

NoneType = type(None)


class PinMessageMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        notify: bool = True,
    ) -> None:
        """Execute the pin message MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :raises RuntimeError: If pinMessage method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("PinMessage method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                pin_message_id=message_id,
                notify_pin=notify,
            ),
        )
