from typing import Optional, cast

from .Base import BaseMaxApiMethod
from ..models.EmojiReaction import EmojiReaction


class RemoveReactionMethod(BaseMaxApiMethod[Optional[EmojiReaction]]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
    ) -> EmojiReaction | None:
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
