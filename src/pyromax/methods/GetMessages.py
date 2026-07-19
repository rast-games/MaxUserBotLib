from typing import cast
from collections.abc import Iterable

from .Base import BaseMaxApiMethod
from ..models import Message


class GetMessagesMethod(BaseMaxApiMethod[list[Message]]):
    async def __call__(
            self,
            chat_id: int,
            message_ids: Iterable[int | str],
    ) -> list[Message]:
        if not self._max_api:
            raise RuntimeError('GetMessages method not bound to MaxApi instance')

        return cast(
            list[Message],
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_ids=message_ids,
            )
        )