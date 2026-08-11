from typing import cast

from .Base import BaseMaxApiMethod


class CloseAllSessionsMethod(BaseMaxApiMethod[bool]):
    async def __call__(self) -> bool:
        """Execute the close all sessions MAX API method.

        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        :raises RuntimeError: If closeAllSessions method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("CloseAllSessions method not bound to MaxApi instance")
        return cast(
            bool,
            await self._max_api.mapper.call_method(
                type(self),
            ),
        )
