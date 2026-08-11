from typing import cast

from .Base import BaseMaxApiMethod

NoneType = type(None)


class SetPresenceMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(self, online: bool) -> None:
        """Execute the set presence MAX API method.

        :param online: The online value.
        :type online: bool
        :raises RuntimeError: If setPresence method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("SetPresence method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                online=online,
            ),
        )
