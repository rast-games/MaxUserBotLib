from typing import cast

from .Base import BaseMaxApiMethod
from ..models.PrivacySettings import PrivacySettings

NoneType = type(None)


class ChangeProfileSettingsMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        privacy_settings: PrivacySettings,
    ) -> None:
        """Execute the change profile settings MAX API method.

        :param privacy_settings: PrivacySettings instance to process.
        :type privacy_settings: PrivacySettings
        :raises RuntimeError: If changeProfileSettings method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError(
                "ChangeProfileSettings method not bound to MaxApi instance"
            )

        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                privacy_settings=privacy_settings,
            ),
        )
