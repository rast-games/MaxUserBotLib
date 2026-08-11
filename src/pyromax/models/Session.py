from typing import Any

from .base import BaseMaxObject


class Session(BaseMaxObject):
    id: int | str | None = None
    device_id: str | None = None
    current: bool | None = None
    user_agent: str | None = None
    app_version: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    platform: str | None = None
    ip: str | None = None
    location: str | None = None
    created: int | None = None
    updated: int | None = None
    last_activity: int | None = None
    options: dict[str, Any] | list[Any] | None = None
    time: int | None = None
    info: str | None = None
