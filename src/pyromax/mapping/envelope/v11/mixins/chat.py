import time
from typing import cast

from .MixinProtocol import MixinProtocol
from .....models import Chat, Message
from ..methods.immutable import CreateChatMethod
from ..payloads.responses import CreateGroupResponse
from ..translate.ToDTO import translate_models


class ChatMixin(MixinProtocol):
    async def create_group(
        self,
        title: str,
        participant_ids: list[int] | None = None,
        notify: bool = True,
        chat_type: str = "CHAT",
        event: str = "new",
        typeof: str = "CONTROL",
    ) -> tuple[Chat, Message] | None:
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
            return None

        mapped_create_chat_message = chat_and_message.message
        mapped_chat = chat_and_message.chat
        for attach in mapped_create_chat_message.attaches:
            attach.chat_id = chat_and_message.chat_id
            attach.message_id = mapped_create_chat_message.id

        mapped_create_chat_message.chat_id = chat_and_message.chat_id

        message = cast(Message, translate_models(mapped_create_chat_message))
        chat = cast(Chat, translate_models(mapped_chat))

        return chat, message
