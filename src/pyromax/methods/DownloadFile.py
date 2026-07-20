from typing import Union

from .Base import BaseMaxApiMethod
from ..models import BaseFileAttachment


class DownloadFileMethod(BaseMaxApiMethod[Union[tuple[bytes, dict[str, str]], tuple[None, None]]]):
    async def __call__(
            self,
            file: BaseFileAttachment
    ) -> tuple[bytes, dict[str, str]] | tuple[None, None]:
        if not self._max_api:
            raise RuntimeError('SendMessage method not bound to MaxApi instance')

        return await self._max_api.mapper.download_file(
            file=file
        )

        # return await self._max_api.mapper.call_method(
        #     type(self),
        #     file=file
        # )
