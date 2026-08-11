from typing import Optional, cast

from .Base import BaseMaxApiMethod
from ..models.EmojiReaction import EmojiReaction


class AddReactionMethod(BaseMaxApiMethod[Optional[EmojiReaction]]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        reaction_id: str,
        reaction_type: str = "EMOJI",
    ) -> EmojiReaction | None:
        """Execute the add reaction MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param reaction_id: Identifier of the reaction.
        :type reaction_id: str
        :param reaction_type: The reaction type value.
        :type reaction_type: str
        :returns: The resulting EmojiReaction | None value.
        :rtype: EmojiReaction | None
        :raises RuntimeError: If addReaction method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("AddReaction method not bound to MaxApi instance")

        return cast(
            EmojiReaction | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                reaction_id=reaction_id,
                reaction_type=reaction_type,
            ),
        )
