from typing import Optional, cast

from .Base import BaseMaxApiMethod
from ..models.EmojiReaction import EmojiReaction


class RemoveReactionMethod(BaseMaxApiMethod[Optional[EmojiReaction]]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
    ) -> EmojiReaction | None:
        """Execute the remove reaction MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :returns: The resulting EmojiReaction | None value.
        :rtype: EmojiReaction | None
        :raises RuntimeError: If removeReaction method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("RemoveReaction method not bound to MaxApi instance")

        return cast(
            EmojiReaction | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
            ),
        )
