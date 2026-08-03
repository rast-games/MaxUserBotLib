from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Contact


class GetUserMethod(BaseMaxApiMethod[Union[Contact, None]]):
    async def __call__(self, user_id: int) -> Contact | None:
        if not self._max_api:
            raise RuntimeError("GetUser method not bound to MaxApi instance")
        return cast(
            Contact | None,
            await self._max_api.mapper.call_method(
                type(self),
                user_id=user_id,
            ),
        )
