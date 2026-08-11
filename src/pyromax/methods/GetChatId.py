from typing import cast

from .Base import BaseMaxApiMethod

# from ..models import Contact


class GetChatIdMethod(BaseMaxApiMethod[int]):
    async def __call__(self, first_user_id: int, second_user_id: int) -> int:
        """Execute the get chat id MAX API method.

        :param first_user_id: Identifier of the first user.
        :type first_user_id: int
        :param second_user_id: Identifier of the second user.
        :type second_user_id: int
        :returns: The resulting int value.
        :rtype: int
        :raises RuntimeError: If getChatId method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("GetChatId method not bound to MaxApi instance")
        return cast(
            int,
            await self._max_api.mapper.call_method(
                type(self),
                first_user_id=first_user_id,
                second_user_id=second_user_id,
            ),
        )
