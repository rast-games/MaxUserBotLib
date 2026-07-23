from typing import cast, Literal

from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION
from ...payloads.requests import (
    SendMessageRequest,
    GetMessagesRequest,
    EditMessageRequest,
    GetChatHistoryRequest,
    DeleteMessageRequest,
    PinMessageRequest,
    AddReactionRequest,
    RemoveReactionRequest,
    GetReactionsRequest,
    ReactionInfoRequest,
    ReadMessageRequest,
)
from ...translate.FromDTO import reverse_translate_message
from ...payloads.models import MessageMappingModel, MessageLinkMappingModel


class SendMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SEND_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION

        main_link = self.args.get("link")
        request.payload = SendMessageRequest(
            chat_id=self.args["chat_id"],
            message=MessageMappingModel(
                text=self.args.get("text"),
                cid=self.args["cid"],
                attaches=self.args["attaches"] if self.args["attaches"] else [],
                elements=(
                    self.args["elements"]
                    if self.args["text"] and self.args["elements"]
                    else None
                ),
                link=(
                    MessageLinkMappingModel(
                        type=main_link.type,
                        message_id=main_link.message_id,
                        chat_id=main_link.chat_id,
                        message=reverse_translate_message(main_link.message),
                    )
                    if main_link
                    else None
                ),
            ),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class EditMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.EDIT_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = EditMessageRequest(
            chat_id=self.args["chat_id"],
            message_id=self.args["message_id"],
            text=self.args.get("text"),
            elements=(
                self.args["elements"]
                if self.args["text"] and self.args["elements"]
                else None
            ),
            attachments=self.args["attaches"] if self.args["attaches"] else [],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetMessagesMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_MESSAGES
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetMessagesRequest(
            message_ids=self.args["message_ids"],
            chat_id=self.args["chat_id"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetChatHistoryMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_CHAT_MESSAGES_PER_CHUNK
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetChatHistoryRequest(
            chat_id=self.args["chat_id"],
            from_=self.args["from_time"],
            forward=self.args["forward"],
            backward=self.args["backward"],
            backward_time=self.args["backward_time"],
            forward_time=self.args["forward_time"],
            item_type=self.args["item_type"],
            get_messages=self.args["get_messages"],
            get_chat=self.args["get_chat"],
            interactive=self.args["interactive"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class DeleteMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.DELETE_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = DeleteMessageRequest(
            chat_id=self.args["chat_id"],
            message_ids=self.args["message_ids"],
            for_me=cast(bool, self.args.get("for_me")),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class PinMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.PIN_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = PinMessageRequest(
            chat_id=self.args["chat_id"],
            notify_pin=self.args["notify_pin"],
            pin_message_id=self.args["pin_message_id"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class AddReactionMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.ADD_REACTION
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = AddReactionRequest(
            chat_id=self.args["chat_id"],
            message_id=self.args["message_id"],
            reaction=ReactionInfoRequest(
                reaction_type=self.args.get("reaction_type", "EMOJI"),
                id=self.args["reaction_id"],
            ),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class RemoveReactionMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.REMOVE_REACTION
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = RemoveReactionRequest(
            chat_id=self.args["chat_id"],
            message_id=self.args["message_id"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetReactionsMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_REACTIONS
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetReactionsRequest(
            chat_id=self.args["chat_id"],
            message_ids=self.args["message_ids"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class ReadMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.READ_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ReadMessageRequest(
            type=cast(Literal["READ_MESSAGE", "READ_REACTION"], self.args["type"]),
            chat_id=self.args["chat_id"],
            message_id=self.args["message_id"],
            mark=self.args["mark"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    "SendMessageMethod",
    "EditMessageMethod",
    "GetMessagesMethod",
    "GetChatHistoryMethod",
    "DeleteMessageMethod",
    "PinMessageMethod",
    "AddReactionMethod",
    "RemoveReactionMethod",
    "GetReactionsMethod",
    "ReadMessageMethod",
]
