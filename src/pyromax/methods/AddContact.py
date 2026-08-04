from typing import cast

from .Base import BaseMaxApiMethod
from ..models import Contact


class AddContactMethod(BaseMaxApiMethod[Contact]):
    async def __call__(self, contact_id: int) -> Contact:
        if not self._max_api:
            raise RuntimeError("AddContact method not bound to MaxApi instance")
        return cast(
            Contact,
            await self._max_api.mapper.call_method(
                type(self),
                contact_id=contact_id,
            ),
        )
