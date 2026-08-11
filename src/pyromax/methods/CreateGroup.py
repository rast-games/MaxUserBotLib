from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat
from ..models.Message import Message


class CreateGroupMethod(
    BaseMaxApiMethod[Union[tuple[Chat, Message], tuple[None, None]]]
):
    async def __call__(
        self,
        title: str,
        participant_ids: list[int] | None = None,
        notify: bool = True,
        chat_type: str = "CHAT",
        event: str = "new",
        typeof: str = "CONTROL",
    ) -> tuple[Chat, Message] | tuple[None, None]:
        """Execute the create group MAX API method.

        :param title: The title value.
        :type title: str
        :param participant_ids: Identifiers of the participant objects.
        :type participant_ids: list[int] | None
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :param chat_type: The chat type value.
        :type chat_type: str
        :param event: Incoming event to process.
        :type event: str
        :param typeof: Attachment class that determines the upload type.
        :type typeof: str
        :returns: The resulting tuple[Chat, Message] | tuple[None, None] value.
        :rtype: tuple[Chat, Message] | tuple[None, None]
        :raises RuntimeError: If createGroup method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("CreateGroup method not bound to MaxApi instance")

        return cast(
            tuple[Chat, Message] | tuple[None, None],
            await self._max_api.mapper.call_method(
                type(self),
                title=title,
                participant_ids=participant_ids,
                notify=notify,
                chat_type=chat_type,
                event=event,
                typeof=typeof,
            ),
        )
