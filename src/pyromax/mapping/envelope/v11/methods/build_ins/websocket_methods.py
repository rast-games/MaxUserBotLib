from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine


from .base import LoginBuildInMappingMethod
from ......exceptions import MapperApiError
from ..immutable import GetUserDataMethod
from ...payloads.responses import ChoiceLoginVariantResponse

if TYPE_CHECKING:
    from ...Mapper import Mapper
    from ...payloads.responses import MetadataResponse


class WebSocketLoginBuildInMappingMethod(LoginBuildInMappingMethod):
    async def __call__(
        self,
        mapper: Mapper,
        *args: Any,
        url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
        sms_auth: bool = False,
        code_getter: Callable[..., Coroutine[Any, Any, int]] | None = None,
        **kwargs: Any,
    ) -> ChoiceLoginVariantResponse:
        if sms_auth:
            return await self._resolve_sms_auth(
                mapper=mapper,
                code_getter=code_getter,
            )

        metadata = await mapper.request_qr()
        if metadata is None:
            raise MapperApiError("Metadata not given for login")
        track_id = metadata.track_id
        await self._resolve_qr(
            mapper=mapper, url_callback=url_callback, metadata=metadata
        )

        return await mapper.confirm_qr(track_id=track_id)
