from __future__ import annotations
from typing import Optional, Literal, Any, TYPE_CHECKING

from .base import BaseMaxObject
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
        attaches: list[  #type: ignore[valid-type]
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

        if self._max_api is None:
            raise RuntimeError("Message Model not linked to MaxApi instance")

        return await self._max_api(
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
