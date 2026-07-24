from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Chat


class JoinGroupMethod(BaseMaxApiMethod[Chat]):
    async def __call__(self, link: str) -> Chat:
        if not self._max_api:
            raise RuntimeError("JoinGroup method not bound to MaxApi instance")

        return cast(
            Chat,
            await self._max_api.mapper.call_method(type(self), link=link),
        )


class JoinChannelMethod(BaseMaxApiMethod[Chat]):
    async def __call__(self, link: str) -> Chat:
        if not self._max_api:
            raise RuntimeError("JoinGroup method not bound to MaxApi instance")

        return cast(
            Chat,
            await self._max_api.mapper.call_method(type(self), link=link),
        )
