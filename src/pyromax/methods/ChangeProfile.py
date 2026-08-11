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
        """Execute the change profile MAX API method.

        :param first_name: The first name value.
        :type first_name: str
        :param last_name: The last name value.
        :type last_name: str | None
        :param description: The description value.
        :type description: str | None
        :param photo: The photo value.
        :type photo: bytes | None
        :param file_name: The file name value.
        :type file_name: str | None
        :param photo_token: The photo token value.
        :type photo_token: str | None
        :returns: The resulting Profile value.
        :rtype: Profile
        :raises RuntimeError: If changeProfile method not bound to MaxApi instance.
        """
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
