from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine
import asyncio

from ......utils import Backoff
from ......exceptions import MapperApiError
from .base import LoginBuildInMappingMethod
from ...payloads.responses import ChoiceLoginVariantResponse

from ..immutable import GetUserDataMethod

if TYPE_CHECKING:
    from ...Mapper import Mapper
    from ......models import RegistrationConfig


class SocketLoginBuildInMappingMethod(LoginBuildInMappingMethod):
    async def __call__(
        self,
        mapper: Mapper,
        *args: Any,
        login_backoff: Backoff | None = None,
        code_getter: Callable[..., Coroutine[Any, Any, int]] | None = None,
        sms_auth: bool = True,
        url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
        use_mobile_fingerprint: bool = True,
        registration_config: RegistrationConfig | None = None,
        **kwargs: Any,
    ) -> ChoiceLoginVariantResponse:
        if sms_auth:
            return await self._resolve_sms_auth(
                mapper=mapper,
                code_getter=code_getter,
                use_mobile_fingerprint=use_mobile_fingerprint,
                registration_config=registration_config,
            )
        else:
            metadata = await mapper.request_qr()
            if metadata is None:
                raise MapperApiError("Metadata must be provided")
            await self._resolve_qr(
                mapper=mapper,
                metadata=metadata,
                url_callback=url_callback,
            )
            return await mapper.confirm_qr(track_id=metadata.track_id)
