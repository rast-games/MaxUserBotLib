from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class ChangeGroupProfileMethod(BaseMaxApiMethod[Union[Chat, None]]):

    async def __call__(
        self,
        chat_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Chat | None:
        """Execute the change group profile MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param name: The name value.
        :type name: str | None
        :param description: The description value.
        :type description: str | None
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        :raises RuntimeError: If changeGroupProfile method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ChangeGroupProfile method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                name=name,
                description=description,
            ),
        )
