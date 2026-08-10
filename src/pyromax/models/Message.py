from __future__ import annotations
from typing import Optional, Literal, Any, TYPE_CHECKING

from .base import BaseMaxObject
from .ReadState import ReadState
from .EmojiReaction import EmojiReaction
from .Attachments import BaseFileAttachment


class MessageLink(BaseMaxObject):
    type: str | None = None
    message: Message | None = None
    message_id: int | str | None = None
    chat_id: int | None = None


class Message(BaseMaxObject):
    message_id: int | str
    chat_id: int
    time: int
    type: str | None
    sender_id: int | None = None
    status: Literal["EDITED", "REPLY", "USER", "REMOVED", "SHARE", "OTHER"] = "USER"
    text: str | None
    cid: int | None
    elements: list[dict[str, Any]] | None = None
    link: MessageLink | None = None

    if TYPE_CHECKING:
        from .Attachments import (
            VideoAttachment,
            VoiceAttachment,
            VideoNoteAttachment,
            FileAttachment,
            PhotoAttachment,
            BaseFileAttachment,
        )
        from .Poll import Poll

        from typing import Never

        attaches: list[  # type: ignore[valid-type]
            VideoAttachment
            | VideoNoteAttachment
            | VoiceAttachment
            | FileAttachment
            | PhotoAttachment
            | Poll[Never]
            | Any
        ]
    else:
        attaches: list[Any] | None = None

    async def answer(
        self,
        text: str | None = None,
        attaches: list[BaseFileAttachment] | None = None,
        link: MessageLink | None = None,
    ) -> Any:
        from ..methods import SendMessageMethod

        return await self.max_api(
            class_of_method=SendMessageMethod,
            text=text,
            chat_id=self.chat_id,
            attaches=attaches,
            link=link,
        )

    async def reply(
        self,
        text: str | None = None,
        attaches: list[BaseFileAttachment] | None = None,
    ) -> Any:
        link = MessageLink(
            type="REPLY",
            message_id=self.message_id,
        )

        return await self.answer(
            text=text,
            attaches=attaches,
            link=link,
        )

    async def forward(
        self,
        chat_id: int,
        *,
        notify: bool = True,
    ) -> Message | None:
        return await self.max_api.forward_message(
            from_chat_id=self.chat_id,
            to_chat_id=chat_id,
            message_id=self.message_id,
            notify=notify,
        )

    async def pin(self, notify_pin: bool = True) -> None:
        return await self.max_api.pin_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            notify=notify_pin,
        )

    async def edit(
        self,
        text: str | None = None,
        attachments: list[BaseFileAttachment] | None = None,
    ) -> Message:
        return await self.max_api.edit_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            attachments=attachments,
        )

    async def delete(self, for_me: bool = False) -> None:
        return await self.max_api.delete_messages(
            chat_id=self.chat_id,
            message_ids=[self.message_id],
            for_me=for_me,
        )

    async def read(self) -> ReadState:
        return await self.max_api.read_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
        )

    async def react(self, reaction: str) -> EmojiReaction | None:
        return await self.max_api.add_reaction(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reaction_id=reaction,
        )

    async def unreact(self) -> EmojiReaction | None:
        return await self.max_api.remove_reaction(
            chat_id=self.chat_id,
            message_id=self.message_id,
        )

    async def get_reactions(self) -> dict[str, EmojiReaction] | None:
        return await self.max_api.get_reactions(
            chat_id=self.chat_id,
            message_ids=[self.message_id],
        )
