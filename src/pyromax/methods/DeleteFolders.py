from typing import cast, Any

from .Base import BaseMaxApiMethod
from ..models.Folder import FolderUpdate


class DeleteFoldersMethod(BaseMaxApiMethod[FolderUpdate]):
    async def __call__(
        self,
        folder_ids: list[str],
    ) -> FolderUpdate:
        if not self._max_api:
            raise RuntimeError("DeleteFolders method not bound to MaxApi instance")

        return cast(
            FolderUpdate,
            await self._max_api.mapper.call_method(
                type(self),
                folder_ids=folder_ids,
            ),
        )
