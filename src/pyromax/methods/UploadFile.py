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
