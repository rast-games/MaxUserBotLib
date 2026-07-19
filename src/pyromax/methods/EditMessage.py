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
            **kwargs: Any
    ) -> Message:
        if not self._max_api:
            raise RuntimeError('EditMessage method not bound to MaxApi instance')

        return cast(
            Message,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                attaches=attaches,
                **kwargs,
            )
        )