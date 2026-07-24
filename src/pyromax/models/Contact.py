from pydantic import Field

from .base import BaseMaxObject
from .Name import Name


class Contact(BaseMaxObject):
    first_name: str = ""
    last_name: str = ""
    names: list[Name] = Field(default_factory=list)
    id: int
    description: str = ""
    phone: str | None = None
    avatar_url: str | None = None
    raw_avatar_url: str | None = None
    photo_id: str | None = None
    country: str | None = None
    account_status: int | None = None
    email: str | None = None
    registration_time: int | None = None
