from typing import Any, cast

from .Base import BaseMaxApiMethod
from ..models import Message, BaseFileAttachment


class EditMessageMethod(BaseMaxApiMethod[Message]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        text: str | None = None,
        attaches: list[BaseFileAttachment] | None = None,
        **kwargs: Any,
    ) -> Message:
        """Execute the edit message MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param text: Message or textual content.
        :type text: str | None
        :param attaches: Attachments associated with the message.
        :type attaches: list[BaseFileAttachment] | None
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting Message value.
        :rtype: Message
        :raises RuntimeError: If editMessage method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("EditMessage method not bound to MaxApi instance")

        return cast(
            Message,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                attaches=attaches,
                **kwargs,
            ),
        )
