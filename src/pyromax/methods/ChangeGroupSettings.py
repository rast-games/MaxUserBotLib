from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models.Chat import Chat


class ChangeGroupSettingsMethod(BaseMaxApiMethod[Union[Chat, None]]):

    async def __call__(
        self,
        chat_id: int,
        all_can_pin_message: bool | None = None,
        only_owner_can_change_icon_title: bool | None = None,
        only_admin_can_add_member: bool | None = None,
        only_admin_can_call: bool | None = None,
        members_can_see_private_link: bool | None = None,
    ) -> Chat | None:
        """Execute the change group settings MAX API method.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param all_can_pin_message: The all can pin message value.
        :type all_can_pin_message: bool | None
        :param only_owner_can_change_icon_title: The only owner can change icon title value.
        :type only_owner_can_change_icon_title: bool | None
        :param only_admin_can_add_member: The only admin can add member value.
        :type only_admin_can_add_member: bool | None
        :param only_admin_can_call: The only admin can call value.
        :type only_admin_can_call: bool | None
        :param members_can_see_private_link: The members can see private link value.
        :type members_can_see_private_link: bool | None
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        :raises RuntimeError: If changeGroupSettings method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError(
                "ChangeGroupSettings method not bound to MaxApi instance"
            )

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                all_can_pin_message=all_can_pin_message,
                only_owner_can_change_icon_title=only_owner_can_change_icon_title,
                only_admin_can_add_member=only_admin_can_add_member,
                only_admin_can_call=only_admin_can_call,
                members_can_see_private_link=members_can_see_private_link,
            ),
        )
