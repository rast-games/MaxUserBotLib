from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine


import qrcode


from ..immutable import TrackLoginMethod, GetMetadataForLoginMethod, StartSMSAuthMethod, VerifySMSCodeMethod
from ......exceptions import MapperApiError
from ...payloads.responses import (TrackLoginResponse, MetadataResponse, StartSMSAuthResponse, TwoFactorLoginResponse,
                                   MetadataResponse, ChoiceLoginVariantResponse)
from ...constants import DEFAULT_BACKOFF_CONFIG
from ......utils import Backoff

if TYPE_CHECKING:
    from ...Mapper import Mapper



class BaseBuildInMappingMethod(ABC):
    @abstractmethod
    async def __call__(self, mapper: Mapper, *args: Any, **kwargs: Any) -> Any: pass


class LoginBuildInMappingMethod(BaseBuildInMappingMethod):
    @abstractmethod
    async def __call__(
            self,
            mapper: Mapper,
            *args: Any,
            login_backoff: Backoff | None = None,
            **kwargs: Any
    ) -> ChoiceLoginVariantResponse: pass
        # raise NotImplementedError()

    @staticmethod
    async def _track_login(
            mapper: Mapper,
            track_id: str,
            polling_interval: int | float,
    ) -> None:

        not_logged = True
        while not_logged:
            await asyncio.sleep(polling_interval)

            response = await mapper.send_raw_with_running_wait(
                method=TrackLoginMethod(
                    track_id=track_id
                ),
                # return_exception=True
            )

            track_data = TrackLoginResponse(
                **response.payload
            )

            if track_data is None:
                raise RuntimeError('Track login failed.')

            if track_data.status is None:
                raise RuntimeError("Track status is missing in response")


            if track_data.status and track_data.status.expires_at < time.time() or track_data.error or track_data.error_message or track_data.localized_message:
                msg = '''
                Time for login expired
                    '''
                raise TimeoutError(msg)


            if track_data.status.login_available:
                not_logged = False



    async def _get_metadata(
            self,
            mapper: Mapper,
    ) -> MetadataResponse:
        response = await mapper.send_raw(
            method=GetMetadataForLoginMethod(),
            check_errors=True
        )
        metadata = MetadataResponse(**response.payload)

        return metadata

    async def _resolve_qr(
            self,
            mapper: Mapper,
            metadata: MetadataResponse,
            url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,

    ) -> None:

        if not url_callback:
            async def url_callback(url: str) -> None:
                """
                Creating a QR code scanned by max. It is displayed immediately in the console

                Args:
                    url - authorization url

                """

                qr = qrcode.QRCode()
                qr.add_data(url)

                qr.make(fit=True)
                qr.print_ascii(invert=True)

        url = metadata.qr_link
        track_id = metadata.track_id
        await url_callback(url)

        await self._track_login(
            mapper=mapper,
            polling_interval=metadata.polling_interval,
            track_id=track_id,
        )


    @staticmethod
    async def _resolve_sms_auth(
            mapper: Mapper,
            code_getter: Callable[..., Coroutine[Any, Any, int]] | None = None
    ) -> ChoiceLoginVariantResponse:
        auth_type = 'START_AUTH'
        temp_token: str | None = None
        sms_backoff = Backoff(config=DEFAULT_BACKOFF_CONFIG)
        while True:
            try:
                response = await mapper.send_raw(
                    method=StartSMSAuthMethod(
                        phone=mapper.phone,
                        type=auth_type
                    ),
                    check_errors=True
                )
                auth_response = StartSMSAuthResponse(**response.payload)
                temp_token = auth_response.token

                break
            except MapperApiError as e:
                error = e.error
                match error:
                    case 'verify.code.wrong':
                        mapper.log(20, 'SMS code wrong, resending...')
                        auth_type = "RESEND"
                        continue
                    case 'error.limit.violate':
                        mapper.log(20, 'SMS limit violate')
                        raise e
                    case 'error.code.attempt.limit':
                        mapper.log(20, 'SMS code limit reached, over login')
                        raise e
                    case 'auth.request.forbidden':
                        mapper.log(20, 'SMS auth request forbidden for this transport')
                        raise e
                    case _:
                        mapper.log(20, f'Error while login with SMS code: {error}')
                        raise e

        verify_code: int | str
        password_challenge_response: TwoFactorLoginResponse | None = None
        if temp_token is None:
            raise RuntimeError('temp token not given')
        while True:
            try:
                if code_getter is not None:
                    verify_code = await code_getter()
                else:
                    verify_code = await asyncio.to_thread(input, 'Write a sms code: ')
                check_response = await mapper.send_raw(
                    method=VerifySMSCodeMethod(
                        temp_token=temp_token,
                        auth_token_type='CHECK_CODE',
                        verify_code=str(verify_code),
                    ),
                    check_errors=True
                )
                password_challenge_response = TwoFactorLoginResponse(
                    **check_response.payload
                )
                break
            except MapperApiError as e:
                mapper.log(40, f'Error while login with SMS code: {e}')
                error = e.error
                match error:
                    case 'error.limit.violate':
                        mapper.log(20, 'SMS code limit reached, over login')
                        raise e
                    case 'auth.request.forbidden':
                        mapper.log(20, 'SMS auth request forbidden for this transport')
                        raise e
                    case _:
                        mapper.log(20, f'Error while login with SMS code: {error}')
                        raise e

        if password_challenge_response is None:
            raise RuntimeError('Password challenge response not found.')

        choice = ChoiceLoginVariantResponse(payload=password_challenge_response)
        return choice


