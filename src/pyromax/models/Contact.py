from typing import Any
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
    update_time: int | None = None
    status: str | None = None
    gender: str | int | None = None
    link: str | None = None
    web_app: dict[str, Any] | str | None = None
    menu_button: dict[str, Any] | None = None
    options: list[str] = Field(default_factory=list)


    async def add_contact(self) -> "Contact":
        return await self.max_api.add_contact(
            contact_id=self.id,
        )


    async def remove_contact(self) -> None:
        return await self.max_api.remove_contact(
            contact_id=self.id,
        )


    async def get_chat_id(self, contact_id: int) -> int:
        return await self.max_api.get_chat_id(
            first_user_id=contact_id,
            second_user_id=self.id,
        )