from typing import cast

from .Base import BaseMaxApiMethod

NoneType = type(None)


class Check2FaMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
    ) -> None:
        if not self._max_api:
            raise RuntimeError("Check2Fa method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
            ),
        )
