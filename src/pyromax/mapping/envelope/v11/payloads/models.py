from __future__ import annotations
from abc import abstractmethod, ABC
import random
from typing import Annotated, Literal, Any, ClassVar, TYPE_CHECKING, Self
from uuid import uuid4

from pydantic import Field, BeforeValidator, AliasChoices, AliasPath, model_validator

from .....models import (
    BaseFileAttachment,
    PhotoAttachment,
    VideoAttachment,
    FileAttachment,
    ShareAttachment,
    BaseUserAgent,
    ControlAttachment,
)
from .shared import CamelCaseModel
from .....utils import (
    get_random_device_id_numeric,
    get_random_device_id,
    get_random_app_version_and_build_number,
)
from .....config import WEB_APP_VERSION, WEB_SCREEN, DEFAULT_WEB_HEADER_USER_AGENT

if TYPE_CHECKING:
    from .requests import (
        BaseUserAgentRequest,
        AppUserAgentRequest,
        WebUserAgentRequest,
        MobileUserAgentRequest,
    )

import time


class BaseUserAgentMappingModel(BaseUserAgent, CamelCaseModel, ABC):
    device_type: str
    locale: str = "ru"
    device_id: str = Field(default_factory=lambda: get_random_device_id())
    timezone: str = "Europe/Moscow"
    device_locale: str = "ru"
    os_version: str = "Windows 10 Version 22H2"
    device_name: str = "WINDOWS10"

    @abstractmethod
    def to_request(self) -> BaseUserAgentRequest: ...

    @classmethod
    @abstractmethod
    def get_random_user_agent(cls, **kwargs: Any) -> Self: ...


class WebUserAgentMappingModel(BaseUserAgentMappingModel):
    device_type: str = "WEB"
    device_id: str = Field(default=get_random_device_id(), exclude=True)
    header_user_agent: str = DEFAULT_WEB_HEADER_USER_AGENT
    app_version: str = WEB_APP_VERSION
    screen: str = WEB_SCREEN

    def to_request(self) -> WebUserAgentRequest:
        device_id = self.device_id
        from .requests import WebUserAgentRequest

        return WebUserAgentRequest(device_id=device_id, user_agent=self)

    @classmethod
    def get_random_user_agent(cls, **kwargs: Any) -> WebUserAgentMappingModel:
        from .....config import LOCALE_TIMEZONES

        locale, timezone = random.choice(LOCALE_TIMEZONES)
        args: dict[str, Any] = {
            "locale": locale,
            "timezone": timezone,
        }
        for key, value in kwargs.items():
            args[key] = value
        return cls(**args)


class AppUserAgentMappingModel(BaseUserAgentMappingModel):
    device_type: str = "DESKTOP"
    screen: str = "2.0x"
    device_id: str = Field(default_factory=get_random_device_id_numeric, exclude=True)
    client_session_id: int = Field(
        default_factory=lambda: random.randint(1, 30), exclude=True
    )
    build_number: int
    app_version: str

    @model_validator(mode="before")
    @classmethod
    def set_random_version_pair(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if (
                "build_number" in data
                and "app_version" not in data
                or "app_version" in data
                and "build_number" not in data
            ):
                raise ValueError("you need give pair from build_number and app_version")

            if "build_number" not in data and "app_version" not in data:
                app_ver, build_num = get_random_app_version_and_build_number()
                data["build_number"] = build_num
                data["app_version"] = app_ver
        return data

    def to_request(self) -> AppUserAgentRequest:
        client_session_id = self.client_session_id
        device_id = self.device_id
        from .requests import AppUserAgentRequest

        return AppUserAgentRequest(
            device_id=device_id, client_session_id=client_session_id, user_agent=self
        )

    @classmethod
    def get_random_user_agent(cls, **kwargs: Any) -> AppUserAgentMappingModel:
        from .....config import APP_VERSIONS, LOCALE_TIMEZONES

        app_version, build_number = random.choice(APP_VERSIONS)
        locale, timezone = random.choice(LOCALE_TIMEZONES)

        args: dict[str, Any] = {
            "build_number": build_number,
            "app_version": app_version,
            "locale": locale,
            "timezone": timezone,
        }

        for key, value in kwargs.items():
            args[key] = value
        return cls(**args)


class MobileUserAgentMappingModel(AppUserAgentMappingModel):
    device_type: str = "ANDROID"
    os_version: str = "Android 13"
    arch: str = "arm64-v8a"
    device_name: str = "Samsung SM-A525F"
    push_device_type: str = "GCM"
    app_version: str = "26.14.1"
    build_number: int = 6686
    device_id: str = Field(default_factory=lambda: str(uuid4()), exclude=True)
    mt_instance_id: str = Field(
        default_factory=lambda: str(uuid4()),
        exclude=True,
        alias="mt_instanceid",
        serialization_alias="mt_instanceid",
    )

    def to_request(self) -> MobileUserAgentRequest:
        from .requests import MobileUserAgentRequest

        return MobileUserAgentRequest(
            device_id=self.device_id,
            user_agent=self,
            mt_instanceid=self.mt_instance_id,
            client_session_id=self.client_session_id,
        )

    @classmethod
    def get_random_user_agent(cls, **kwargs: Any) -> MobileUserAgentMappingModel:
        from .....config import ANDROID_DEVICES, APP_VERSIONS, LOCALE_TIMEZONES

        device_name, os_version, screen, arch = random.choice(ANDROID_DEVICES)
        app_version, build_number = random.choice(APP_VERSIONS)
        locale, timezone = random.choice(LOCALE_TIMEZONES)

        args: dict[str, Any] = {
            "device_name": device_name,
            "os_version": os_version,
            "screen": screen,
            "arch": arch,
            "build_number": build_number,
            "app_version": app_version,
            "locale": locale,
            "timezone": timezone,
        }
        for key, value in kwargs.items():
            args[key] = value

        return cls(**args)


class AuthMappingModel(CamelCaseModel):
    token: str
    chats_count: int
    interactive: bool
    chats_sync: int
    contacts_sync: int
    presence_sync: int
    drafts_sync: int
    # user_agent: dict[Any, Any] = {
    #         'deviceType': 'IOS',
    #         'locale': 'ru',
    #         'timezone': 'Asia/Yakutsk',
    #         'deviceLocale': 'ru',
    #         'osVersion': '17.5',
    #         'deviceName': 'iPhone',
    #         'screen': '411dpi 411dpi 1080x2400',
    #         'buildNumber': 6678,
    #         'appVersion': '26.12.0',
    #         'arch': 'arm64-v8a',
    #         'pushDeviceType': 'GCM'
    #     }


class PasswordConfig(CamelCaseModel):
    pass_max_len: int
    pass_min_len: int
    hint_max_len: int


class NameMappingModel(CamelCaseModel):
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    type: str = ""


class ContactMappingModel(CamelCaseModel):
    account_status: int
    country: str | None = None
    description: str = ""
    email: str | None = None
    id: int
    names: list[NameMappingModel]
    options: list[str]
    phone: int | None = None
    photo_id: int | None = None
    update_time: int
    registration_time: int
    base_url: str | None = None
    base_raw_url: str | None = None


class ProfileMappingModel(CamelCaseModel):
    contact: ContactMappingModel
    profile_options: list[Any]


class ChangeGroupSettingsModel(CamelCaseModel):
    only_owner_can_change_icon_title: bool | None = Field(
        default=None,
        serialization_alias="ONLY_OWNER_CAN_CHANGE_ICON_TITLE",
    )
    all_can_pin_message: bool | None = Field(
        default=None,
        serialization_alias="ALL_CAN_PIN_MESSAGE",
    )
    only_admin_can_add_member: bool | None = Field(
        default=None,
        serialization_alias="ONLY_ADMIN_CAN_ADD_MEMBER",
    )
    only_admin_can_call: bool | None = Field(
        default=None,
        serialization_alias="ONLY_ADMIN_CAN_CALL",
    )
    members_can_see_private_link: bool | None = Field(
        default=None,
        serialization_alias="MEMBERS_CAN_SEE_PRIVATE_LINK",
    )


class BaseFileMappingModel(BaseFileAttachment, CamelCaseModel, ABC):
    is_attach: ClassVar[bool] = True
    is_downloadable: ClassVar[bool] = True
    message_id: str | None = None
    uploaded: bool = Field(default=False, exclude=True)
    chat_id: int | None = None
    type: str = Field(
        serialization_alias="_type",
        validation_alias=AliasChoices(AliasPath("type"), AliasPath("_type")),
    )

    @property
    @abstractmethod
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        return {
            "messageId": self.message_id,
            "chatId": self.chat_id,
        }

    @property
    @abstractmethod
    def to_payload(self) -> list[dict[str, Any]]:
        pass


class PhotoMappingModel(BaseFileMappingModel, PhotoAttachment):
    photo_token: str
    photo_id: int | str | None = None
    base_url: str | None = None
    height: int | None = None
    width: int | None = None
    preview_data: Any | None = None

    # never will be called
    @property
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        return None

    @property
    def to_payload(self) -> list[dict[str, Any]]:
        from .requests import PhotoToPayloadRequest

        photos = []
        photos.append(
            PhotoToPayloadRequest(
                type="PHOTO", photo_token=self.photo_token
            ).model_dump(by_alias=True)
        )
        return photos


class VideoMappingModel(BaseFileMappingModel, VideoAttachment):
    token: str
    video_id: int
    video_type: int | None = None
    duration: int | None = None
    height: int | None = None
    width: int | None = None
    preview_data: Any | None = None
    trumbnail: str | None = None

    @property
    def to_payload(self) -> list[dict[str, Any]]:
        from .requests import VideoToPayloadRequest

        return [
            VideoToPayloadRequest(
                type="VIDEO", video_id=self.video_id, token=self.token
            ).model_dump(by_alias=True),
        ]

    @property
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        res = super().get_payload_to_get_link
        if res is None:
            raise RuntimeError("get_payload_to_get_link should return dict")
        res.update(
            {
                "videoId": self.video_id,
                "token": self.token,
            }
        )

        return res


class FileMappingModel(BaseFileMappingModel, FileAttachment):
    token: str | None = None
    file_id: int
    size: int | None = None
    name: str | None = None

    @property
    def to_payload(self) -> list[dict[str, Any]]:
        from .requests import FileToPayloadRequest

        return [
            FileToPayloadRequest(
                type="FILE",
                file_id=self.file_id,
            ).model_dump(by_alias=True),
        ]

    @property
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        res = super().get_payload_to_get_link
        if res is None:
            raise RuntimeError("get_payload_to_get_link should return dict")
        res.update(
            {
                "fileId": self.file_id,
            }
        )

        return res


class ShareMappingModel(BaseFileMappingModel, ShareAttachment):
    image: PhotoMappingModel | None = None
    description: str | None = None
    contentLevel: bool | None = None
    share_id: int
    title: str | None = None
    url: str | None = None
    is_downloadable: ClassVar[bool] = False

    @property
    def to_payload(self) -> list[dict[str, Any]]:
        return []

    @property
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        raise TypeError("Try a download Share attachment")


class ControlMappingModel(BaseFileMappingModel, ControlAttachment):
    event: str
    title: str | None = None
    user_ids: list[str | int] | None = None
    is_attach: ClassVar[bool] = False
    is_downloadable: ClassVar[bool] = False
    uploaded: bool = True

    @property
    def to_payload(self) -> list[dict[str, Any]]:
        return []

    @property
    def get_payload_to_get_link(self) -> dict[str, Any] | None:
        raise TypeError("Try a download Control attachment")


class MessageLinkMappingModel(CamelCaseModel):
    type: str | None = None
    message: MessageMappingModel | None = None
    message_id: int | str | None = None
    chat_id: int | None = None


StatusType = Literal["EDITED", "REPLY", "USER", "REMOVED"]


def validate_status(v: Any) -> Any:
    if v not in ("EDITED", "REPLY", "USER", "REMOVED"):
        return "USER"
    return v


class MessageMappingModel(CamelCaseModel):
    cid: int = -round(time.time() * 1000)
    attaches: list[
        VideoMappingModel
        | PhotoMappingModel
        | FileMappingModel
        | ShareMappingModel
        | ControlMappingModel
        | Any
    ] = []
    sender: int | None = None
    chat_id: int | None = None
    id: str | int | None = Field(default=None, serialization_alias="message_id")
    time: int | None = None
    type: str | None = None
    text: str | None = None
    status: Annotated[StatusType, BeforeValidator(validate_status)] = "USER"
    elements: list[dict[str, Any]] | None = None
    link: MessageLinkMappingModel | None = None


class ReactionInfoMappingModel(CamelCaseModel):
    your_reaction: str | None = None
    total_count: int | None = None
    counters: list[dict[str, Any]] | None = None


class ReadStateMappingModel(CamelCaseModel):
    unread: int
    mark: int


MessageLinkMappingModel.model_rebuild()


class ChatMappingModel(CamelCaseModel):
    id: int
    type: Literal["DIALOG", "CHAT", "CHANNEL"]
    status: str
    owner: int
    participants: dict[int, int] = Field(default_factory=dict)
    title: str | None = None
    base_raw_icon_url: str | None = None
    base_icon_url: str | None = None
    last_message: MessageMappingModel | None = None
    last_event_time: int = 0
    last_delayed_update_time: int = 0
    last_fire_delayed_error_time: int = 0
    created: int = 0
    new_messages: int = 0
    link: str | None = None
    access: Literal["PUBLIC", "PRIVATE", "SECRET"] | None = None
    restrictions: int | None = None
    pinned_message: MessageMappingModel | None = None
    participants_count: int = 0
    description: str | None = None
    options: dict[str, bool] | int | None = None
    join_time: int = 0
    invited_by: int | None = None
    modified: int = 0
    messages_count: int = 0
    has_bots: bool | None = None
    prev_message_id: int | None = None
    admin_participants: dict[int, dict[Any, Any]] = Field(default_factory=dict)
    admins: list[int] = Field(default_factory=list)
    cid: int | None = None


class CreateGroupAttachMappingModel(CamelCaseModel):
    type: Literal["CONTROL"] = Field(default="CONTROL", serialization_alias="_type")
    event: Literal["new"] = "new"
    chat_type: Literal["CHAT", "DIALOG", "CHANNEL"] = "CHAT"
    title: str
    user_ids: list[int]


class CreateGroupMessageMappingModel(CamelCaseModel):
    cid: int = Field(default_factory=lambda: int(time.time() * 1000))
    attaches: list[CreateGroupAttachMappingModel]


# structures that are needed in both requests and responses at the same time


class TrackLoginMappingModel(CamelCaseModel):
    track_id: str


# end of structures for responses and requests at the same time
