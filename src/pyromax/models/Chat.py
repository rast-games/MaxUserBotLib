from typing import Literal, Any

from pydantic import Field

from .base import BaseMaxObject
from .Message import Message


class Chat(BaseMaxObject):
    id: int
    type: Literal["DIALOG", "CHAT", "CHANNEL"]
    status: str
    owner: int
    participants: dict[int, int] = Field(default_factory=dict)
    title: str | None = None
    base_raw_icon_url: str | None = None
    base_icon_url: str | None = None
    last_message: Message | None = None
    last_event_time: int = 0
    last_delayed_update_time: int = 0
    last_fire_delayed_error_time: int = 0
    created: int = 0
    new_messages: int = 0
    link: str | None = None
    access: Literal["PUBLIC", "PRIVATE", "SECRET"] | None = None
    restrictions: int | None = None
    pinned_message: Message | None = None
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
