from typing import cast
from .Base import BaseMaxApiMethod

NoneType = type(None)


class DeleteChatMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        chat_id: int,
        last_event_time: int | None = None,
        for_all: bool = True,
    ) -> None:
        """Execute the delete chat MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param last_event_time: The last event time value.
        :type last_event_time: int | None
        :param for_all: The for all value.
        :type for_all: bool
        :raises RuntimeError: If deleteChat method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("DeleteChat method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                last_event_time=last_event_time,
                for_all=for_all,
            ),
        )
