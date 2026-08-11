from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class InviteUsersToGroupMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(
        self,
        chat_id: int,
        user_ids: list[int],
        show_history: bool = True,
    ) -> Chat | None:
        """Execute the invite users to group MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_ids: Identifiers of the users.
        :type user_ids: list[int]
        :param show_history: The show history value.
        :type show_history: bool
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        :raises RuntimeError: If inviteUsersToGroup method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("InviteUsersToGroup method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                user_ids=user_ids,
                show_history=show_history,
            ),
        )
