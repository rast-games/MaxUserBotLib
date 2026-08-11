from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact
from ..models.ContactInfo import ContactInfo


class ImportContactsMethod(BaseMaxApiMethod[list[Contact]]):
    async def __call__(self, contacts: list[ContactInfo]) -> list[Contact]:
        """Execute the import contacts MAX API method.

        :param contacts: Collection of contacts.
        :type contacts: list[ContactInfo]
        :returns: The resulting collection.
        :rtype: list[Contact]
        :raises RuntimeError: If importContacts method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ImportContacts method not bound to MaxApi instance")
        return cast(
            list[Contact],
            await self._max_api.mapper.call_method(
                type(self),
                contacts=contacts,
            ),
        )
