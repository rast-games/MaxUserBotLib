from typing import cast

from .Base import BaseMaxApiMethod

NoneType = type(None)


class DeleteMessagesMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        chat_id: int,
        message_ids: list[str] | list[int],
        for_me: bool = False,
    ) -> None:
        if not self._max_api:
            raise RuntimeError("DeleteMessages method not bound to MaxApi instance")

        return cast(
            NoneType,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_ids=message_ids,
                for_me=for_me,
            ),
        )
