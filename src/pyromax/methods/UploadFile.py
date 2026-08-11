from typing import Any


from .Base import BaseMaxApiMethod
from ..models import BaseFileAttachment


class UploadFileMethod(BaseMaxApiMethod[list[BaseFileAttachment | Any]]):
    async def __call__(
        self,
        data: bytes | None,
        typeof: type[BaseFileAttachment],
        *args: Any,
        **kwargs: Any,
    ) -> list[BaseFileAttachment | Any]:
        """Execute the upload file MAX API method.

        :param data: Contextual data passed through the processing pipeline.
        :type data: bytes | None
        :param typeof: Attachment class that determines the upload type.
        :type typeof: type[BaseFileAttachment]
        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting collection.
        :rtype: list[BaseFileAttachment | Any]
        :raises RuntimeError: If uploadFile method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("UploadFile method not bound to MaxApi instance")

        return await self._max_api.mapper.upload_file(
            data,
            typeof,
            # *args,
            **kwargs,
        )

        # return await self._max_api.mapper.call_method(
        #     type(self),
        #     data,
        #     typeof,
        #     # *args,
        #     **kwargs
        # )
