from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact


class SearchByPhoneMethod(BaseMaxApiMethod[Contact]):
    async def __call__(self, phone: str) -> Contact:
        """Execute the search by phone MAX API method.

        :param phone: Phone number in the format accepted by MAX.
        :type phone: str
        :returns: The resulting Contact value.
        :rtype: Contact
        :raises RuntimeError: If searchByPhone method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("SearchByPhone method not bound to MaxApi instance")

        return cast(
            Contact,
            await self._max_api.mapper.call_method(
                type(self),
                phone=phone,
            ),
        )
