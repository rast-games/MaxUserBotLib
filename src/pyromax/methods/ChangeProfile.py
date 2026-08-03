from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Profile import Profile


class ChangeProfileMethod(BaseMaxApiMethod[Profile]):
    async def __call__(
        self,
        first_name: str,
        last_name: str | None = None,
        description: str | None = None,
        photo: bytes | None = None,
        file_name: str | None = None,
        photo_token: str | None = None,
    ) -> Profile:
        if not self._max_api:
            raise RuntimeError("ChangeProfile method not bound to MaxApi instance")

        return cast(
            Profile,
            await self._max_api.mapper.call_method(
                type(self),
                first_name=first_name,
                last_name=last_name,
                description=description,
                photo=photo,
                file_name=file_name,
                photo_token=photo_token,
            ),
        )
