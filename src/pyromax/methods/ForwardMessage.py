from typing import cast, Optional

from .Base import BaseMaxApiMethod
from ..models import Message



class ForwardMessageMethod(BaseMaxApiMethod[Optional[Message]]):
    async def __call__(
            self,
            message_id: int | str,
            from_chat_id: int,
            to_chat_id: int,
    ) -> Message | None:
        if not self._max_api:
            raise RuntimeError('ForwardMessage method not bound to MaxApi instance')
        return cast(
            Message | None,
            await self._max_api.mapper.call_method(
                type(self),
                message_id=message_id,
                from_chat_id=from_chat_id,
                to_chat_id=to_chat_id,
            )
        )