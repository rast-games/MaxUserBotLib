from typing import cast, Any


from ...exceptions import MapperApiError
from ...methods import (
    ChangeProfileMethod,
    CreateFolderMethod,
    GetFoldersMethod,
    UpdateFolderMethod,
    DeleteFoldersMethod,
    CloseAllSessionsMethod,
    LogoutMethod,
    SetPresenceMethod,
    ChangeProfileSettingsMethod,
)
from ...models import (
    Profile,
    FolderUpdate,
    FolderList,
    PrivacySettings,
)
from .CoreMixinsProtocol import CoreMixinsProtocol


class UserMixin(CoreMixinsProtocol):
    async def change_profile(
        self,
        first_name: str,
        last_name: str | None = None,
        description: str | None = None,
        photo: bytes | None = None,
        file_name: str | None = None,
        photo_token: str | None = None,
    ) -> Profile:
        """Change profile.

        :param first_name: The first name.
        :type first_name: str
        :param last_name: The last name.
        :type last_name: str | None
        :param description: The description.
        :type description: str | None
        :param photo: The photo data.
        :type photo: bytes | None
        :param file_name: The file name or photo file.
        :type file_name: str | None
        :param photo_token: The photo token value.
        :type photo_token: str | None
        :returns: The resulting Profile.
        :rtype: Profile
        """

        return cast(
            Profile,
            await self(
                ChangeProfileMethod,
                first_name=first_name,
                last_name=last_name,
                description=description,
                photo=photo,
                file_name=file_name,
                photo_token=photo_token,
            ),
        )

    async def create_folder(
        self,
        title: str,
        chat_include: list[int],
        filters: list[Any] | None = None,
        folder_id: str | None = None,
    ) -> FolderUpdate:
        """Create folder.

        :param title: The title of folder.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int]
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param folder_id: Identifier of the folder.
        :type folder_id: str | None
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """

        return cast(
            FolderUpdate,
            await self(
                CreateFolderMethod,
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
            ),
        )

    async def get_folders(self, folder_sync: int = 0) -> FolderList:
        """Retrieve folders.

        :param folder_sync: Synchronization marker. Leave as ``0`` for the initial load..
        :type folder_sync: int
        :returns: The resulting FolderList.
        :rtype: FolderList
        """

        return cast(
            FolderList,
            await self(
                GetFoldersMethod,
                folder_sync=folder_sync,
            ),
        )

    async def update_folder(
        self,
        folder_id: str,
        title: str,
        chat_include: list[int] | None = None,
        filters: list[Any] | None = None,
        options: list[Any] | None = None,
    ) -> FolderUpdate:
        """Update folder.

        :param folder_id: Identifier of the folder.
        :type folder_id: str
        :param title: The title of folder.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int] | None
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param options: Collection of options.
        :type options: list[Any] | None
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """

        return cast(
            FolderUpdate,
            await self(
                UpdateFolderMethod,
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
                options=options,
            ),
        )

    async def delete_folders(
        self,
        folder_ids: list[str],
    ) -> FolderUpdate:
        """Delete folders.

        :param folder_ids: Identifiers of the folders.
        :type folder_ids: list[str]
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """

        return cast(
            FolderUpdate,
            await self(
                DeleteFoldersMethod,
                folder_ids=folder_ids,
            ),
        )

    async def delete_folder(self, folder_id: str) -> FolderUpdate:
        """Delete folder.

        :param folder_id: Identifier of the folder.
        :type folder_id: str
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """
        return await self.delete_folders(folder_ids=[folder_id])

    async def close_all_sessions(self) -> bool:
        """Close all sessions.

        :returns: ``True`` if the server accepted the request; otherwise ``False``.
        :rtype: bool
        """
        return cast(
            bool,
            await self(
                CloseAllSessionsMethod,
            ),
        )

    async def logout(self) -> None:
        """Logout."""
        return cast(None, await self(LogoutMethod))

    async def set_presence(self, online: bool) -> None:
        """Set presence.

        :param online: The online value.
        :type online: bool
        """
        return cast(
            None,
            await self(
                SetPresenceMethod,
                online=online,
            ),
        )

    async def change_profile_settings(self, privacy_settings: PrivacySettings) -> None:
        """Update the account privacy settings.

        :param privacy_settings: Privacy settings to apply to the account.

        :raises ValueError: If updating the privacy settings fails.

        :type privacy_settings: PrivacySettings
        """

        try:
            return cast(
                None,
                await self(
                    ChangeProfileSettingsMethod,
                    privacy_settings=privacy_settings,
                ),
            )
        except MapperApiError as e:
            raise ValueError("Change profile settings failed") from e
