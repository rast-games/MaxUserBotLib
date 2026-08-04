from typing import cast

from .Base import BaseMaxApiMethod
from ..models import Contact, ContactInfo


class ImportContactsMethod(BaseMaxApiMethod[list[Contact]]):
    async def __call__(self, contacts: list[ContactInfo]) -> list[Contact]:
        if not self._max_api:
            raise RuntimeError("ImportContacts method not bound to MaxApi instance")
        return cast(
            list[Contact],
            await self._max_api.mapper.call_method(
                type(self),
                contacts=contacts,
            ),
        )
