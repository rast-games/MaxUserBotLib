from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Chat


class RevokeInviteLinkMethod(BaseMaxApiMethod[Union[Chat]]):
    async def __call__(self, chat_id: int) -> Chat:
        if not self._max_api:
            raise RuntimeError("ResolveGroupByLink method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
            ),
        )
