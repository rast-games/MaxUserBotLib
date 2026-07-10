from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine
import asyncio

from ......utils import Backoff
from ......exceptions import MapperApiError
from .base import LoginBuildInMappingMethod
from ...payloads.responses import (
    ChoiceLoginVariantResponse
)

from ..immutable import (
    GetUserDataMethod
)


if TYPE_CHECKING:
    from ...Mapper import Mapper


class SocketLoginBuildInMappingMethod(LoginBuildInMappingMethod):
    async def __call__(
            self,
            mapper: Mapper,
            *args: Any,
            login_backoff: Backoff | None = None,
            code_getter: Callable[..., Coroutine[Any, Any, int]] | None = None,
            sms_auth: bool = True,
            # metadata: MetadataResponse | None = None,
            url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
            **kwargs: Any
    ) -> ChoiceLoginVariantResponse:
        if sms_auth:
            return await self._resolve_sms_auth(
                mapper=mapper,
                code_getter=code_getter,
            )
        else:
            metadata = await self._get_metadata(mapper)
            if metadata is None:
                raise MapperApiError('Metadata must be provided')
            await self._resolve_qr(
                mapper=mapper,
                metadata=metadata,
                url_callback=url_callback,
            )
            response = await mapper.send_raw_with_running_wait(
                method=GetUserDataMethod(
                    track_id=metadata.track_id
                ),
            )
            payload = response.payload
            user = ChoiceLoginVariantResponse(
                payload=payload,
            )
            return user

