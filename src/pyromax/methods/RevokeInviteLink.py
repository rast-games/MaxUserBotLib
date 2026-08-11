from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class RevokeInviteLinkMethod(BaseMaxApiMethod[Chat]):
    async def __call__(self, chat_id: int) -> Chat:
        """Execute the revoke invite link MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Chat value.
        :rtype: Chat
        :raises RuntimeError: If resolveGroupByLink method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ResolveGroupByLink method not bound to MaxApi instance")

        return cast(
            Chat,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
            ),
        )
