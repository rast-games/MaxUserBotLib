from typing import cast, Literal

from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION
from ...payloads.requests import (
    CreateChatRequest,
    ChatMemberOperationRequest,
    ChangeGroupSettingsRequest,
    ChangeGroupProfileRequest,
)
from ...payloads.models import (
    CreateGroupMessageMappingModel,
    CreateGroupAttachMappingModel,
    ChangeGroupSettingsModel,
)


class CreateChatMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SEND_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = CreateChatRequest(
            notify=self.args.get("notify", True),
            message=CreateGroupMessageMappingModel(
                cid=self.args["cid"],
                attaches=[
                    CreateGroupAttachMappingModel(
                        type=cast(Literal["CONTROL"], self.args.get("type", "CONTROL")),
                        event=cast(Literal["new"], self.args.get("event", "new")),
                        chat_type=cast(
                            Literal["CHAT", "DIALOG", "CHANNEL"],
                            self.args.get("chat_type", "CHAT"),
                        ),
                        title=self.args["title"],
                        user_ids=self.args.get("user_ids", []),
                    ),
                ],
            ),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class ChatMemberOperationMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.OPERATION_WITH_CHAT_MEMBER
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ChatMemberOperationRequest(
            chat_id=self.args["chat_id"],
            user_ids=self.args["user_ids"],
            show_history=self.args.get("show_history"),
            operation=self.args["operation"],
            clean_msg_period=self.args.get("clean_msg_period"),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class ChangeGroupSettingsMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.CHAT_UPDATE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ChangeGroupSettingsRequest(
            chat_id=self.args["chat_id"],
            options=ChangeGroupSettingsModel(
                only_owner_can_change_icon_title=self.args.get(
                    "only_owner_can_change_icon_title"
                ),
                all_can_pin_message=self.args.get("all_can_pin_message"),
                only_admin_can_add_member=self.args.get("only_admin_can_add_member"),
                only_admin_can_call=self.args.get("only_admin_can_call"),
                members_can_see_private_link=self.args.get(
                    "members_can_see_private_link"
                ),
            ),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class ChangeGroupProfileMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.CHAT_UPDATE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ChangeGroupProfileRequest(
            chat_id=self.args["chat_id"],
            theme=self.args.get("name"),
            description=self.args.get("description"),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    "CreateChatMethod",
    "ChatMemberOperationMethod",
    "ChangeGroupSettingsMethod",
    "ChangeGroupProfileMethod",
]
