from typing import cast

from .Base import BaseMaxApiMethod
from ..models import Contact


class SearchByPhoneMethod(BaseMaxApiMethod[Contact]):
    async def __call__(self, phone: str) -> Contact:
        if not self._max_api:
            raise RuntimeError("SearchByPhone method not bound to MaxApi instance")

        return cast(
            Contact,
            await self._max_api.mapper.call_method(
                type(self),
                phone=phone,
            ),
        )
