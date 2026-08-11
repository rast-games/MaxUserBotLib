from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact


class AddContactMethod(BaseMaxApiMethod[Contact]):
    async def __call__(self, contact_id: int) -> Contact:
        """Execute the add contact MAX API method.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        :returns: The resulting Contact value.
        :rtype: Contact
        :raises RuntimeError: If addContact method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("AddContact method not bound to MaxApi instance")
        return cast(
            Contact,
            await self._max_api.mapper.call_method(
                type(self),
                contact_id=contact_id,
            ),
        )
