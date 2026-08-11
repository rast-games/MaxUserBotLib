from typing import cast, Any

from .Base import BaseMaxApiMethod
from ..models import FolderUpdate


class UpdateFolderMethod(BaseMaxApiMethod[FolderUpdate]):
    async def __call__(
        self,
        folder_id: str,
        title: str,
        chat_include: list[int] | None = None,
        filters: list[Any] | None = None,
        options: list[Any] | None = None,
    ) -> FolderUpdate:
        """Execute the update folder MAX API method.

        :param folder_id: Identifier of the folder.
        :type folder_id: str
        :param title: The title value.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int] | None
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param options: Collection of options.
        :type options: list[Any] | None
        :returns: The resulting FolderUpdate value.
        :rtype: FolderUpdate
        :raises RuntimeError: If updateFolder method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("UpdateFolder method not bound to MaxApi instance")

        return cast(
            FolderUpdate,
            await self._max_api.mapper.call_method(
                type(self),
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
                options=options,
            ),
        )
