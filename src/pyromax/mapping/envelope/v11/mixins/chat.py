import time
from typing import cast

from .MixinProtocol import MixinProtocol
from .....exceptions import MapperApiError, ParseMaxApiError
from .....models import Chat, Message
from ..methods.immutable import (
    CreateChatMethod,
    ChatMemberOperationMethod,
    ChangeGroupSettingsMethod,
    ChangeGroupProfileMethod,
    JoinGroupMethod,
)
from ..payloads.responses import CreateGroupResponse, ChatContainsResponse
from ..translate.ToDTO import translate_models


class ChatMixin(MixinProtocol):
    def _cache_chat(self, chat: Chat) -> Chat:
        if self.max_api is None:
            raise RuntimeError("Mapper not bound to max_api instance")

        if self.max_api.chats is None:
            self.max_api.chats = [chat]
            return chat

        for inx, cached in enumerate(self.max_api.chats):
            if cached.id == chat.id:
                self.max_api.chats[inx] = chat
                return chat

        self.max_api.chats.append(chat)
        return chat

    async def create_group(
        self,
        title: str,
        participant_ids: list[int] | None = None,
        notify: bool = True,
        chat_type: str = "CHAT",
        event: str = "new",
        typeof: str = "CONTROL",
    ) -> tuple[Chat, Message] | tuple[None, None]:
        if participant_ids is None:
            participant_ids = []
        response = await self.send(
            method=CreateChatMethod(
                title=title,
                user_ids=participant_ids,
                notify=notify,
                chat_type=chat_type,
                event=event,
                type=typeof,
                cid=int(time.time() * 1000),
            )
        )
        chat_and_message = CreateGroupResponse(**response.payload)
        if chat_and_message.chat is None:
            return None, None

        mapped_create_chat_message = chat_and_message.message
        mapped_chat = chat_and_message.chat
        for attach in mapped_create_chat_message.attaches:
            attach.chat_id = chat_and_message.chat_id
            attach.message_id = mapped_create_chat_message.id

        mapped_create_chat_message.chat_id = chat_and_message.chat_id

        message = cast(Message, translate_models(mapped_create_chat_message))
        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)

        return chat, message

    async def invite_users_to_group(
        self,
        chat_id: int,
        user_ids: list[int] | list[str],
        show_history: bool = True,
    ) -> Chat | None:
        response = await self.send(
            method=ChatMemberOperationMethod(
                chat_id=chat_id,
                user_ids=user_ids,
                show_history=show_history,
                operation="add",
            )
        )

        mapped_chat = ChatContainsResponse(**response.payload).chat
        if mapped_chat is None:
            return None

        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat

    async def remove_users_from_group(
        self,
        chat_id: int,
        user_ids: list[int] | list[str],
        clean_msg_period: int,
    ) -> Chat | None:
        response = await self.send(
            method=ChatMemberOperationMethod(
                chat_id=chat_id,
                user_ids=user_ids,
                clean_msg_period=clean_msg_period,
                operation="remove",
            )
        )

        mapped_chat = ChatContainsResponse(**response.payload).chat
        if mapped_chat is None:
            return None

        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat

    async def change_group_settings(
        self,
        chat_id: int,
        all_can_pin_message: bool | None = None,
        only_owner_can_change_icon_title: bool | None = None,
        only_admin_can_add_member: bool | None = None,
        only_admin_can_call: bool | None = None,
        member_can_see_private_link: bool | None = None,
    ) -> Chat | None:
        response = await self.send(
            method=ChangeGroupSettingsMethod(
                chat_id=chat_id,
                all_can_pin_message=all_can_pin_message,
                only_owner_can_change_icon_title=only_owner_can_change_icon_title,
                only_admin_can_add_member=only_admin_can_add_member,
                only_admin_can_call=only_admin_can_call,
                member_can_see_private_link=member_can_see_private_link,
            )
        )

        mapped_chat = ChatContainsResponse(**response.payload).chat
        if mapped_chat is None:
            return None

        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat

    async def change_group_profile(
        self,
        chat_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Chat | None:
        response = await self.send(
            method=ChangeGroupProfileMethod(
                chat_id=chat_id,
                name=name,
                description=description,
            )
        )
        mapped_chat = ChatContainsResponse(**response.payload).chat
        if mapped_chat is None:
            return None

        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat

    async def _join_chat(self, link: str) -> Chat:
        response = await self.send(method=JoinGroupMethod(link=link))
        mapped_chat = ChatContainsResponse(**response.payload).chat
        if mapped_chat is None:
            raise MapperApiError("JoinGroup request doesn't return a chat")
        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat

    @staticmethod
    def _prepare_chat_join_link(link: str) -> str | None:
        idx = link.find("join/")
        return link[idx:] if idx != -1 else None

    async def join_group(self, link: str) -> Chat:
        parsed_link = self._prepare_chat_join_link(link)
        if parsed_link is None:
            raise ValueError("Join link invalid")
        return await self._join_chat(parsed_link)

    async def join_channel(self, link: str) -> Chat:
        parsed_link = self._prepare_chat_join_link(link)

        return await self._join_chat(parsed_link or link)
