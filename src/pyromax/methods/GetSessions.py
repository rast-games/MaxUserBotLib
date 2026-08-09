from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Session import Session


class GetSessionsMethod(BaseMaxApiMethod[list[Session]]):
    async def __call__(self) -> list[Session]:
        if not self._max_api:
            raise RuntimeError("GetSessions method not bound to MaxApi instance")

        return cast(
            list[Session],
            await self._max_api.mapper.call_method(
                type(self),
            ),
        )
