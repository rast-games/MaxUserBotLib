from typing import cast

from .Base import BaseMaxApiMethod
from ..models import FolderList


class GetFoldersMethod(BaseMaxApiMethod[FolderList]):
    async def __call__(self, folder_sync: int = 0) -> FolderList:
        """Execute the get folders MAX API method.

        :param folder_sync: The folder sync value.
        :type folder_sync: int
        :returns: The resulting FolderList value.
        :rtype: FolderList
        :raises RuntimeError: If getFolders method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("GetFolders method not bound to MaxApi instance")

        return cast(
            FolderList,
            await self._max_api.mapper.call_method(
                type(self),
                folder_sync=folder_sync,
            ),
        )
