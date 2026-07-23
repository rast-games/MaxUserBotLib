from typing import cast

from .Base import BaseMaxApiMethod
from ..models.ReadState import ReadState


class ReadMessageMethod(BaseMaxApiMethod[ReadState]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        mark: int,
        typeof: str = "READ_MESSAGE",
    ) -> ReadState:
        if not self._max_api:
            raise RuntimeError("ReadMessage method not bound to MaxApi instance")
        return cast(
            ReadState,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                mark=mark,
                typeof=typeof,
            ),
        )
