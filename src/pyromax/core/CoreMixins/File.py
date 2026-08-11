from typing import cast, Any

from ...methods import (
    DownloadFileMethod,
    UploadFileMethod,
)

from ...models import BaseFileAttachment
from .CoreMixinsProtocol import CoreMixinsProtocol


class FileMixin(CoreMixinsProtocol):

    async def download_file(
        self, file: BaseFileAttachment
    ) -> tuple[bytes, dict[str, str]] | tuple[None, None]:
        """Download file.

        :param file: File attachment to process.
        :type file: BaseFileAttachment
        :returns: The resulting tuple[bytes, dict[str, str]] | tuple[None, None] value is request headers | None semantic.
        :rtype: tuple[bytes, dict[str, str]] | tuple[None, None]
        """
        return cast(
            tuple[bytes, dict[str, str]] | tuple[None, None],
            await self(
                DownloadFileMethod,
                file=file,
            ),
        )

    async def upload_file(
        self, data: bytes | None, typeof: type[BaseFileAttachment], **kwargs: Any
    ) -> list[BaseFileAttachment | Any]:
        """Upload file.

        :param data: Contextual data passed through the processing pipeline.
        :type data: bytes | None
        :param typeof: Attachment class that determines the upload type.
        :type typeof: type[BaseFileAttachment]
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting collection.
        :rtype: list[BaseFileAttachment | Any]
        """
        # from ..models import BaseFileAttachment

        return cast(
            list[BaseFileAttachment | Any],
            await self(
                UploadFileMethod,
                data=data,
                typeof=typeof,
                **kwargs,
            ),
        )
