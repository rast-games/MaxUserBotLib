from typing import cast

from .Base import BaseMaxApiMethod
from ..models import FolderList


class GetFoldersMethod(BaseMaxApiMethod[FolderList]):
    async def __call__(self, folder_sync: int = 0) -> FolderList:
        if not self._max_api:
            raise RuntimeError("GetFolders method not bound to MaxApi instance")

        return cast(
            FolderList,
            await self._max_api.mapper.call_method(
                type(self),
                folder_sync=folder_sync,
            ),
        )
