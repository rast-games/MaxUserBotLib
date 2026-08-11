from collections.abc import Iterable
from typing import cast

from .Base import BaseMaxApiMethod
from ..models import ChannelPermissions

NoneType = type(None)


class AddAdminMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self, chat_id: int, user_id: int, permissions: Iterable[ChannelPermissions]
    ) -> None:
        """Execute the add admin MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_id: Identifier of the user.
        :type user_id: int
        :param permissions: Collection of permissions.
        :type permissions: Iterable[ChannelPermissions]
        :raises RuntimeError: If addAdmin method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("AddAdmin method not bound to MaxApi instance")

        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
            ),
        )
