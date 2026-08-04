from typing import cast

from .Base import BaseMaxApiMethod

# from ..models import Contact


class GetChatIdMethod(BaseMaxApiMethod[int]):
    async def __call__(self, first_user_id: int, second_user_id: int) -> int:
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
