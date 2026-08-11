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
        """Execute the delete messages MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: list[str] | list[int]
        :param for_me: The for me value.
        :type for_me: bool
        :raises RuntimeError: If deleteMessages method not bound to MaxApi instance.
        """
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
