from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class ResolveGroupByLinkMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(self, link: str) -> Chat | None:
        if not self._max_api:
            raise RuntimeError("ResolveGroupByLink method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                link=link,
            ),
        )
