from typing import Optional, cast

from .Base import BaseMaxApiMethod
from ..models.EmojiReaction import EmojiReaction


class GetReactionsMethod(
    BaseMaxApiMethod[Optional[dict[str, EmojiReaction] | dict[str, EmojiReaction]]]
):
    async def __call__(
        self,
        chat_id: int,
        message_ids: list[int] | list[str],
    ) -> dict[str, EmojiReaction] | None:
        """Execute the get reactions MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: list[int] | list[str]
        :returns: The resulting dict[str, EmojiReaction] | None value.
        :rtype: dict[str, EmojiReaction] | None
        :raises RuntimeError: If getReactions method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("GetReactions method not bound to MaxApi instance")

        return cast(
            dict[str, EmojiReaction] | dict[str, EmojiReaction] | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_ids=message_ids,
            ),
        )
