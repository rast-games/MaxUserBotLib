from typing import cast, Literal

from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION
from ...payloads.requests import CreateChatRequest
from ...payloads.models import (
    CreateGroupMessageMappingModel,
    CreateGroupAttachMappingModel,
)


class CreateChatMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SEND_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = CreateChatRequest(
            notify=self.args.get("notify", True),
            message=CreateGroupMessageMappingModel(
                cid=self.args.get("cid"),
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


__all__ = [
    "CreateChatMethod",
]
