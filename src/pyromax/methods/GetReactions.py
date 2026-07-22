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
