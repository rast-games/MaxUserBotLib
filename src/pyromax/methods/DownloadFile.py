from typing import Union

from .Base import BaseMaxApiMethod
from ..models import BaseFileAttachment


class DownloadFileMethod(
    BaseMaxApiMethod[Union[tuple[bytes, dict[str, str]], tuple[None, None]]]
):
    async def __call__(
        self, file: BaseFileAttachment
    ) -> tuple[bytes, dict[str, str]] | tuple[None, None]:
        """Execute the download file MAX API method.

        :param file: File attachment to process.
        :type file: BaseFileAttachment
        :returns: The resulting tuple[bytes, dict[str, str]] | tuple[None, None] value.
        :rtype: tuple[bytes, dict[str, str]] | tuple[None, None]
        :raises RuntimeError: If downloadFile method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("DownloadFile method not bound to MaxApi instance")

        return await self._max_api.mapper.download_file(file=file)

        # return await self._max_api.mapper.call_method(
        #     type(self),
        #     file=file
        # )
