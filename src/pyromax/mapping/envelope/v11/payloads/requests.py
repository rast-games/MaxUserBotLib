import time
from random import randint
from typing import Any, Literal

from pydantic import Field

from .shared import CamelCaseModel
from .models import (
    BaseUserAgentMappingModel,
    MessageMappingModel,
    WebUserAgentMappingModel,
    AppUserAgentMappingModel,
    MobileUserAgentMappingModel,
    VideoMappingModel,
    PhotoMappingModel,
    FileMappingModel,
    ShareMappingModel,
    CreateGroupMessageMappingModel,
    ChangeGroupSettingsModel,
)


class BaseUserAgentRequest(CamelCaseModel):
    user_agent: BaseUserAgentMappingModel
    device_id: str


class AppUserAgentRequest(BaseUserAgentRequest):
    user_agent: AppUserAgentMappingModel
    device_id: str
    client_session_id: int = Field(default_factory=lambda: randint(1, 70))


class WebUserAgentRequest(BaseUserAgentRequest):
    user_agent: WebUserAgentMappingModel
    device_id: str


class MobileUserAgentRequest(AppUserAgentRequest):
    user_agent: MobileUserAgentMappingModel
    mt_instance_id: str = Field(..., alias="mt_instanceid")


class Resolve2FARequest(CamelCaseModel):
    password: str
    track_id: str


class StartPhoneAuthRequest(CamelCaseModel):
    phone: str
    type: str


class VerifySMSCodeRequest(CamelCaseModel):
    verify_code: str
    token: str
    auth_token_type: str


class SendMessageRequest(CamelCaseModel):
    chat_id: int
    message: MessageMappingModel


class EditMessageRequest(CamelCaseModel):
    chat_id: int
    message_id: str | int
    text: str | None = None
    elements: list[dict[str, Any]] | None = None
    attachments: list[
        VideoMappingModel
        | PhotoMappingModel
        | FileMappingModel
        | ShareMappingModel
        | Any
    ] = []


class GetMessagesRequest(CamelCaseModel):
    chat_id: int
    message_ids: list[int | str]


class GetChatHistoryRequest(CamelCaseModel):
    chat_id: int
    forward: int
    backward: int = 40
    backward_time: int = 0
    forward_time: int = 0
    get_chat: bool = False
    from_: int = Field(serialization_alias="from")
    item_type: Literal["DELAYED", "REGULAR"] = "REGULAR"
    get_messages: bool = True
    interactive: bool = False


class DeleteMessageRequest(CamelCaseModel):
    chat_id: int
    message_ids: list[str | int]
    for_me: bool = False


class PinMessageRequest(CamelCaseModel):
    chat_id: int
    notify_pin: bool = True
    pin_message_id: str | int


class ReactionInfoRequest(CamelCaseModel):
    reaction_type: str = "EMOJI"
    id: str


class AddReactionRequest(CamelCaseModel):
    chat_id: int
    message_id: str | int
    reaction: ReactionInfoRequest


class RemoveReactionRequest(CamelCaseModel):
    chat_id: int
    message_id: str | int


class GetReactionsRequest(CamelCaseModel):
    chat_id: int
    message_ids: list[int] | list[str]


class ReadMessageRequest(CamelCaseModel):
    chat_id: int
    message_id: str | int
    type: Literal["READ_MESSAGE", "READ_REACTION"] = "READ_MESSAGE"
    mark: int = Field(default_factory=lambda: int(time.time() * 1000))


class CreateChatRequest(CamelCaseModel):
    message: CreateGroupMessageMappingModel
    notify: bool = True


class ChatMemberOperationRequest(CamelCaseModel):
    chat_id: int
    user_ids: list[str] | list[int]
    operation: Literal["add", "remove"] = "add"
    show_history: bool | None = None
    clean_msg_period: int | None = None


class ChangeGroupSettingsRequest(CamelCaseModel):
    chat_id: int
    options: ChangeGroupSettingsModel


class KeepAliveRequest(CamelCaseModel):
    interactive: bool = True


# --- Files Requests ---
class CreateCellForFileRequest(CamelCaseModel):
    count: int = 1


class AnyFileRequest(CamelCaseModel):
    type: str = Field(serialization_alias="_type")


class FileToPayloadRequest(AnyFileRequest):
    file_id: int


class PhotoToPayloadRequest(AnyFileRequest):
    photo_token: str


class VideoToPayloadRequest(AnyFileRequest):
    video_id: int
    token: str


class GetFileLinkRequest(CamelCaseModel):
    chat_id: int
    message_id: int


class GetContactRequest(CamelCaseModel):
    contact_ids: list[int]


# --- end Files Requests ---
