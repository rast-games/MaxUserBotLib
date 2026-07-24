import time
from typing import cast

from .MixinProtocol import MixinProtocol
from .....models import Chat, Message
from ..methods.immutable import CreateChatMethod, ChatMemberOperationMethod
from ..payloads.responses import CreateGroupResponse, ChatMemberOperationResponse
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

        mapped_chat = ChatMemberOperationResponse(**response.payload).chat
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

        mapped_chat = ChatMemberOperationResponse(**response.payload).chat
        if mapped_chat is None:
            return None

        chat = cast(Chat, translate_models(mapped_chat))
        self._cache_chat(chat)
        return chat
