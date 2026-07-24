from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Chat


class InviteUsersToGroupMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(
        self,
        chat_id: int,
        user_ids: list[str] | list[int],
        show_history: bool = True,
    ) -> Chat | None:
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
