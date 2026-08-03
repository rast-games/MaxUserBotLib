from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Contact


class GetUsersMethod(BaseMaxApiMethod[list[Contact]]):
    async def __call__(self, user_ids: int) -> list[Contact]:
        if not self._max_api:
            raise RuntimeError("GetUser method not bound to MaxApi instance")
        return cast(
            list[Contact],
            await self._max_api.mapper.call_method(
                type(self),
                user_ids=user_ids,
            ),
        )
