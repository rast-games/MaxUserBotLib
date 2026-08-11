from typing import cast, Any

from .Base import BaseMaxApiMethod
from ..models.Folder import FolderUpdate


class CreateFolderMethod(BaseMaxApiMethod[FolderUpdate]):

    async def __call__(
        self,
        title: str,
        chat_include: list[int],
        filters: list[Any] | None = None,
        folder_id: str | None = None,
    ) -> FolderUpdate:
        """Execute the create folder MAX API method.

        :param title: The title value.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int]
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param folder_id: Identifier of the folder.
        :type folder_id: str | None
        :returns: The resulting FolderUpdate value.
        :rtype: FolderUpdate
        :raises RuntimeError: If createFolder method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("CreateFolder method not bound to MaxApi instance")

        return cast(
            FolderUpdate,
            await self._max_api.mapper.call_method(
                type(self),
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
            ),
        )
