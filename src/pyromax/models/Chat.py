from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, Any, overload, cast

from pydantic import Field

from .base import BaseMaxObject
from .Attachments import BaseFileAttachment
from .Message import Message, MessageLink


class Chat(BaseMaxObject):
    id: int
    type: Literal["DIALOG", "CHAT", "CHANNEL"]
    status: str
    owner: int
    participants: dict[int, int] = Field(default_factory=dict)
    title: str | None = None
    base_raw_icon_url: str | None = None
    base_icon_url: str | None = None
    last_message: Message | None = None
    last_event_time: int = 0
    last_delayed_update_time: int = 0
    last_fire_delayed_error_time: int = 0
    created: int = 0
    new_messages: int = 0
    link: str | None = None
    access: Literal["PUBLIC", "PRIVATE", "SECRET"] | None = None
    restrictions: int | None = None
    pinned_message: Message | None = None
    participants_count: int = 0
    description: str | None = None
    options: dict[str, bool] | int | None = None
    join_time: int = 0
    invited_by: int | None = None
    modified: int = 0
    messages_count: int = 0
    has_bots: bool | None = None
    prev_message_id: int | None = None
    admin_participants: dict[int, dict[Any, Any]] = Field(default_factory=dict)
    admins: list[int] = Field(default_factory=list)
    cid: int | None = None

    async def answer(
        self,
        text: str | None = None,
        link: MessageLink | None = None,
        attaches: list[BaseFileAttachment] | None = None,
        notify: bool = True,
    ) -> Message | None:
        return await self.max_api.send_message(
            chat_id=self.id,
            text=text,
            link=link,
            attaches=attaches,
            notify=notify,
        )

    @overload
    async def history(
        self,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = ...,
        item_type: Literal["DELAYED", "REGULAR"] = ...,
        get_chat: bool = ...,
        get_messages: Literal[True] = True,
        interactive: bool = ...,
    ) -> list[Message]:
        pass

    @overload
    async def history(
        self,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = None,
        item_type: Literal["DELAYED", "REGULAR"] = ...,
        get_chat: bool = ...,
        get_messages: Literal[False] = False,
        interactive: bool = ...,
    ) -> list[str]:
        pass

    @overload
    async def history(
        self,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = None,
        item_type: Literal["DELAYED", "REGULAR"] = ...,
        get_chat: bool = ...,
        get_messages: bool = ...,
        interactive: bool = ...,
    ) -> list[Message] | list[str]:
        pass

    async def history(
        self,
        forward: int = 0,
        backward: int = 40,
        backward_time: int = 0,
        forward_time: int = 0,
        from_time: int | None = None,
        item_type: Literal["DELAYED", "REGULAR"] = "REGULAR",
        get_chat: bool = False,
        get_messages: bool = True,
        interactive: bool = False,
    ) -> list[Message] | list[str]:
        return await self.max_api.get_chat_history(
            chat_id=self.id,
            forward=forward,
            backward=backward,
            backward_time=backward_time,
            forward_time=forward_time,
            from_time=from_time,
            item_type=item_type,
            get_chat=get_chat,
            interactive=interactive,
            get_messages=get_messages,
        )

    async def get_message(self, message_id: int | str) -> Message | None:
        return await self.max_api.get_message(
            chat_id=self.id,
            message_id=message_id,
        )

    async def get_messages(
        self, message_ids: Iterable[int] | Iterable[str]
    ) -> list[Message]:
        return await self.max_api.get_messages(
            chat_id=self.id,
            message_ids=message_ids,
        )

    async def leave(self) -> None:
        """
        leave the chat

        :raises RuntimeError: if chat is DIALOG
        :raises ValueError: if chat type is unknown
        """

        if self.type == "DIALOG":
            raise RuntimeError("Cannot leave dialog")
        elif self.type == "CHAT":
            return await self.max_api.leave_group(
                chat_id=self.id,
            )
        elif self.type == "CHANNEL":
            return await self.max_api.leave_channel(
                chat_id=self.id,
            )
        raise ValueError("Unknown chat type=%s", self.type)

    async def delete(self, for_all: bool = True) -> None:
        return await self.max_api.delete_chat(
            chat_id=self.id,
            for_all=for_all,
        )

    async def invite(
        self, user_ids: list[int], show_history: bool = True
    ) -> Chat | None:
        """
        invite users to chat

        :raises ValueError: if try to invite users to unknown chat
        :raises RuntimeError: if max_api not linked to chat instance
        """

        if self.type == "CHAT":
            return await self.max_api.invite_users_to_group(
                chat_id=self.id,
                user_ids=user_ids,
                show_history=show_history,
            )
        elif self.type == "CHANNEL":
            return await self.max_api.invite_users_to_group(
                chat_id=self.id,
                user_ids=user_ids,
                show_history=show_history,
            )

        raise ValueError("Unknown chat type=%s", self.type)

    async def remove_users(
        self,
        user_ids: list[int],
        clean_msg_period: int = 0,
    ) -> None:
        return await self.max_api.remove_users_from_group(
            chat_id=self.id,
            user_ids=user_ids,
            clean_msg_period=clean_msg_period,
        )

    async def pin_message(self, message_id: str | int, notify_pin: bool = True) -> None:
        return await self.max_api.pin_message(
            chat_id=self.id,
            message_id=message_id,
            notify=notify_pin,
        )

    async def update_settings(
        self,
        all_can_pin_message: bool | None = None,
        only_owner_can_change_icon_title: bool | None = None,
        only_admin_can_add_member: bool | None = None,
        only_admin_can_call: bool | None = None,
        members_can_see_private_link: bool | None = None,
    ) -> None:
        return await self.max_api.change_group_settings(
            chat_id=self.id,
            all_can_pin_message=all_can_pin_message,
            only_admin_can_add_member=only_admin_can_add_member,
            only_admin_can_call=only_admin_can_call,
            members_can_see_private_link=members_can_see_private_link,
            only_owner_can_change_icon_title=only_owner_can_change_icon_title,
        )

    async def revoke_invite_link(self) -> Chat:
        return await self.max_api.revoke_invite_link(chat_id=self.id)

    @property
    def is_dialog(self) -> bool:
        return self.type == "DIALOG"

    @property
    def is_group(self) -> bool:
        return self.type == "CHAT"

    @property
    def is_channel(self) -> bool:
        return self.type == "CHANNEL"
