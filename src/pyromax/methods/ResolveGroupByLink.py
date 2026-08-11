from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class ResolveGroupByLinkMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(self, link: str) -> Chat | None:
        """Execute the resolve group by link MAX API method.

        :param link: Invite, message, or resource link.
        :type link: str
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        :raises RuntimeError: If resolveGroupByLink method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ResolveGroupByLink method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                link=link,
            ),
        )
