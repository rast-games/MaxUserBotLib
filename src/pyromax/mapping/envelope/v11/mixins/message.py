from __future__ import annotations
import logging
from collections.abc import Sequence, Iterable
from typing import TYPE_CHECKING, Any, cast, overload, Literal
from collections.abc import Callable, Coroutine
import time
import asyncio

from ..payloads.models import BaseFileMappingModel, MessageMappingModel
from .....protocol.envelope import Envelope, EnvelopeProtocol
from ..constants import DEFAULT_BACKOFF_CONFIG
from .....utils import clean_and_map, Backoff
from ..methods.immutable import (
    SendMessageMethod,
    EditMessageMethod,
    GetMessagesMethod,
    GetChatHistoryMethod,
    DeleteMessageMethod,
    PinMessageMethod,
)
from .....exceptions import (
    SendMessageFileError,
    SendMessageNotFoundError,
    SendMessageError,
    BackoffError,
    MapperApiError,
)
from ..payloads.responses import (
    SendMessageResponse,
    EditMessageResponse,
    GetMessagesResponse,
    GetChatHistoryResponse,
    GetChatHistoryMessagesResponse,
    GetChatHistoryMessagesIdsResponse,
)
from ..translate.ToDTO import translate_models
from .....models import Message

from .MixinProtocol import MixinProtocol

from .....models import MessageLink

if TYPE_CHECKING:
    pass


class MessageMixin(MixinProtocol):
    async def send_message(
        self,
        chat_id: int,
        text: str | None = None,
        attaches: Sequence[BaseFileMappingModel] | None = None,
        link: MessageLink | None = None,
        parse_tags: bool = True,
        **kwargs: Any,
    ) -> Message | None:
        """

        Raises
        ------
            SendMessageError
        """
        original_attaches = attaches
        if not attaches:
            attaches = []
        attachments = []
        for attach in attaches:
            if hasattr(attach, "is_attach") and attach.is_attach:
                attachments.extend(attach.to_payload)
        backoff = Backoff(config=DEFAULT_BACKOFF_CONFIG)
        if "elements" in kwargs:
            elements = kwargs["elements"]
        else:
            elements = []

        if parse_tags:
            text, _elements = clean_and_map(
                text if text else "",
                ["STRONG", "EMPHASIZED", "UNDERLINE", "STRIKETHROUGH", "QUOTE", "LINK"],
            )
            elements += _elements
        try:
            response = await self.send(
                method=SendMessageMethod(
                    chat_id=chat_id,
                    text=text,
                    cid=-round(time.time() * 1000),
                    attaches=attachments,
                    elements=elements,
                    link=link,
                ),
            )

            try:
                while (
                    error_if_exist := response.model_dump()
                    .get("payload", {})
                    .get("error")
                ):
                    error_message = (
                        response.model_dump().get("payload", {}).get("message")
                    )
                    title = response.model_dump().get("payload", {}).get("title")
                    match error_if_exist:
                        case "attachment.not.ready":
                            response = await self.send(
                                method=SendMessageMethod(
                                    chat_id=chat_id,
                                    text=text,
                                    cid=-round(time.time() * 1000),
                                    attaches=attachments,
                                    elements=elements,
                                    link=link,
                                ),
                            )
                            await backoff.asleep()
                            continue
                        case "proto.payload":
                            raise SendMessageFileError(f"""
                                title: {title},
                                error: {error_if_exist},
                                message: {error_message}
                                """)
                        case "not.found":
                            raise SendMessageNotFoundError(f"""
                                title: {title},
                                error: {error_if_exist},
                                message: {error_message}
                                """)
                        case _:
                            raise SendMessageError(f"""
                                title: {title},
                                error: {error_if_exist},
                                message: {error_message}
                                """)
            except BackoffError:
                raise SendMessageError("Max attempts to send message exceeded")
            response_parsed = SendMessageResponse(**response.payload)
            for attach in response_parsed.message.attaches:
                attach.message_id = response_parsed.message.id
                attach.chat_id = response_parsed.chat_id
                attach.uploaded = True
            for i, attach in enumerate(original_attaches or []):
                if (
                    hasattr(attach, "is_attach")
                    and attach.is_attach
                    and hasattr(attach, "is_downloadable")
                    and attach.is_downloadable
                ):
                    recv_attach = response_parsed.message.attaches[i]
                    for attr, value in recv_attach.__dict__.items():
                        setattr(attach, attr, value)
            mapped_message = response_parsed.message
            mapped_message.chat_id = response_parsed.chat_id
            translated_message = cast(Message, translate_models(mapped_message))
            return translated_message

        except (
            asyncio.CancelledError,
            self.protocol.transport.BASE_EXCEPTION_FOR_TRANSPORT,
        ) as e:
            self._logger.error("Error sending message: %s", e)
            return None
            # raise SendMessageError(
            #     'Transport error while sending message or bot was cancelled'
            # )

    async def forward_message(
        self,
        message_id: int | str,
        to_chat_id: int,
        from_chat_id: int,
    ) -> Message | None:
        """
        Websocket can work with both message id types(str | int), but browser uses str, and if you want mask the use
        userbot, should use str type

        Socket use only int, and server raise exception if you try to send message ids use str type
        """

        # if isinstance(message_id, int):
        #     msg_id = str(message_id)

        link = MessageLink(
            type="FORWARD",
            message_id=message_id,
            chat_id=from_chat_id,
        )

        return await self.send_message(
            chat_id=to_chat_id,
            link=link,
        )

    async def edit_message(
        self,
        chat_id: int,
        message_id: int | str,
        text: str | None = None,
        attaches: Sequence[BaseFileMappingModel] | None = None,
        parse_tags: bool = True,
        **kwargs: Any,
    ) -> Message:
        """
        Websocket can work with both message id types(str | int), but browser uses str, and if you want mask the use
        userbot, should use str type

        Socket use only int, and server raise exception if you try to send message ids use str type
        """

        if not attaches:
            attaches = []
        if "elements" in kwargs:
            elements = kwargs["elements"]
        else:
            elements = []

        attachments = []
        for attach in attaches:
            if hasattr(attach, "is_attach") and attach.is_attach:
                attachments.extend(attach.to_payload)

        if parse_tags:
            text, _elements = clean_and_map(
                text if text else "",
                ["STRONG", "EMPHASIZED", "UNDERLINE", "STRIKETHROUGH", "QUOTE", "LINK"],
            )
            elements += _elements

        response = await self.send(
            method=EditMessageMethod(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                elements=elements,
                attaches=attachments,
            ),
        )

        mapped_edited_message = EditMessageResponse(**response.payload).message

        edited_message = cast(
            Message,
            translate_models(mapped_edited_message),
        )
        edited_message.chat_id = chat_id

        return edited_message

    async def get_messages(
        self,
        chat_id: int,
        message_ids: Iterable[str] | Iterable[int],
    ) -> list[Message]:
        """
        Websocket can work with both message id types(str | int), but browser uses str, and if you want mask the use
        userbot, should use str type

        Socket use only int, and server raise exception if you try to send message ids use str type
        """

        # msg_ids = [str(msg_id) for msg_id in message_ids]
        response = await self.send(
            method=GetMessagesMethod(
                chat_id=chat_id,
                message_ids=message_ids,
            )
        )

        mapped_messages = GetMessagesResponse(**response.payload)
        for message in mapped_messages.messages:
            message.chat_id = mapped_messages.chat_id
        messages = [translate_models(message) for message in mapped_messages.messages]

        return cast(list[Message], messages)

    @overload
    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = ...,
        item_type: str = ...,
        get_chat: bool = ...,
        get_messages: Literal[True] = True,
        interactive: bool = ...,
    ) -> list[Message]:
        pass

    @overload
    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = ...,
        item_type: str = ...,
        get_chat: bool = ...,
        get_messages: Literal[False] = False,
        interactive: bool = ...,
    ) -> list[str]: ...

    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = 0,
        backward: int = 40,
        backward_time: int = 0,
        forward_time: int = 0,
        from_time: int | None = None,
        item_type: str = "REGULAR",
        get_chat: bool = False,
        get_messages: bool = True,
        interactive: bool = False,
    ) -> list[Message] | list[str]:
        # TODO: make return Chat object if get_chat==True, because now its doest make any and its just dummy to remember add this
        response = await self.send(
            method=GetChatHistoryMethod(
                chat_id=chat_id,
                forward=forward,
                backward=backward,
                backward_time=backward_time,
                forward_time=forward_time,
                from_time=from_time or int(time.time() * 1000),
                item_type=item_type,
                get_chat=get_chat,
                get_messages=get_messages,
                interactive=interactive,
            )
        )

        mapped_messages = GetChatHistoryResponse(payload=response.payload)
        if get_messages:
            if not isinstance(mapped_messages.payload, GetChatHistoryMessagesResponse):
                raise MapperApiError(
                    "server return unknown response different from expected"
                )
            for message in mapped_messages.payload.messages:
                message.chat_id = chat_id

            messages = [
                translate_models(message)
                for message in mapped_messages.payload.messages
            ]

            return cast(list[Message], messages) or []
        if not isinstance(mapped_messages.payload, GetChatHistoryMessagesIdsResponse):
            raise MapperApiError(
                "server return unknown response different from expected"
            )
        return mapped_messages.payload.message_ids or []

    async def delete_messages(
        self, chat_id: int, message_ids: list[str] | list[int], for_me: bool = False
    ) -> None:
        """
        Websocket can work with both message id types(str | int), but browser uses str, and if you want mask the use
        userbot, should use str type

        Socket use only int, and server raise exception if you try to send message ids use str type
        """

        await self.send(
            method=DeleteMessageMethod(
                chat_id=chat_id,
                message_ids=message_ids,
                for_me=for_me,
            )
        )

        return None

    async def pin_message(
        self,
        chat_id: int,
        pin_message_id: int | str,
        notify_pin: bool = True,
    ) -> None:
        await self.send(
            method=PinMessageMethod(
                chat_id=chat_id, pin_message_id=pin_message_id, notify_pin=notify_pin
            )
        )
        return None
