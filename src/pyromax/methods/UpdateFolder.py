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
