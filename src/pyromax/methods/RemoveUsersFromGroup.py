from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class RemoveUsersFromGroupMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(
        self,
        chat_id: int,
        user_ids: list[str] | list[int],
        clean_msg_period: int,
    ) -> Chat | None:
        if not self._max_api:
            raise RuntimeError(
                "RemoveUsersFromGroup method not bound to MaxApi instance"
            )

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                user_ids=user_ids,
                clean_msg_period=clean_msg_period,
            ),
        )
