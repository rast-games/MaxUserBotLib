from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .Base import BaseMaxApiMethod
from ..models.Message import Message

if TYPE_CHECKING:
    from ..models import BaseFileAttachment


class SendMessageMethod(BaseMaxApiMethod[Optional[Message]]):
    async def __call__(
        self,
        *,
        chat_id: int,
        text: str | None = None,
        attaches: list[BaseFileAttachment] | None = None,
        notify: bool = True,
        **kwargs: Any,
    ) -> Message | None:
        """Execute the send message MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param text: Message or textual content.
        :type text: str | None
        :param attaches: Attachments associated with the message.
        :type attaches: list[BaseFileAttachment] | None
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting Message | None value.
        :rtype: Message | None
        :raises RuntimeError: If sendMessage method not bound to MaxApi instance.
        """
        if not attaches:
            attaches = []

        if not self._max_api:
            raise RuntimeError("SendMessage method not bound to MaxApi instance")
        return await self._max_api.mapper.send_message(
            chat_id=chat_id,
            text=text,
            attaches=attaches,
            notify=notify,
            **kwargs,
        )

        # return await self._max_api.mapper.call_method(
        #     type(self),
        #     chat_id=chat_id,
        #     text=text,
        #     attaches=attaches,
        #     **kwargs,
        # )
