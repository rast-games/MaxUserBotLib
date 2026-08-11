from typing import cast

from .Base import BaseMaxApiMethod

NoneType = type(None)


class RemoveContactMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(self, contact_id: int) -> None:
        """Execute the remove contact MAX API method.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        :raises RuntimeError: If removeContact method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("RemoveContact method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                contact_id=contact_id,
            ),
        )
