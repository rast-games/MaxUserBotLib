from __future__ import annotations
import logging
import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TYPE_CHECKING, cast
import qrcode


from .....protocol.envelope import Envelope, EnvelopeProtocol
from .....models import (
    Profile,
    Chat,
    Contact,
    Message,
    TwoFactorAction,
    RegistrationConfig,
)
from ..payloads.models import BaseUserAgentMappingModel, ProfileOptionsMappingModel
from ..methods.immutable import (
    SendUserAgentMethod,
    SendAuthTokenMethod,
    GetMetadataForLoginMethod,
    SendKeepAlivePingMethod,
    Resolve2FAMethod,
    StartSMSAuthMethod,
    VerifySMSCodeMethod,
    TrackLoginMethod,
    ConfirmRegistrationMethod,
    GetEmailCodeMethod,
    VerifyEmailMethod,
    SetHintMethod,
    SetPasswordMethod,
    GetTrackIdFor2FAMethod,
    SetTwoFactorMethod,
    GetUserDataMethod,
    CheckPasswordMethod,
    RemoveTwoFactorMethod,
    ApproveQrLoginMethod,
)
from ..payloads.responses import (
    AuthResponse,
    SuccessLoginResponse,
    MetadataResponse,
    ChoiceLoginVariantResponse,
    TwoFactorLoginResponse,
    UserAgentResponse,
    StartSMSAuthResponse,
    TrackLoginResponse,
    ConfirmRegistrationResponse,
    GetTrackIdFor2FAResponse,
)
from ..translate.ToDTO import translate_models
from ..translate.FromDTO import reverse_translate_two_factor_actions
from .....utils import read_token, write_token, Backoff
from .....exceptions import (
    MapperCancelledError,
    RestartMapperError,
    BaseMapperError,
    MapperTransportError,
    MapperApiError,
)
from ..constants import DEFAULT_BACKOFF_CONFIG


from .MixinProtocol import MixinProtocol


class AuthMixin(MixinProtocol):
    async def _send_user_agent(
        self,
        user_agent: BaseUserAgentMappingModel,
    ) -> None:

        response = await self.send_raw(
            method=SendUserAgentMethod(
                user_agent=user_agent,
            )
        )
        calls_seed = UserAgentResponse(**response.payload).calls_seed
        self.calls_seed = calls_seed

    async def _send_auth_token(
        self,
        token: str,
        chats_count: int,
        interactive: bool,
        presence_sync: int,
        chats_sync: int,
        contacts_sync: int,
        drafts_sync: int,
    ) -> None:
        self._logger.debug("sending auth token")
        response = await self.send_raw(
            method=SendAuthTokenMethod(
                token=token,
                chats_count=chats_count,
                interactive=interactive,
                presence_sync=presence_sync,
                chats_sync=chats_sync,
                contacts_sync=contacts_sync,
                drafts_sync=drafts_sync,
            )
        )

        self._logger.debug("recv auth token response")

        auth_model = AuthResponse(**response.payload)

        if self.max_api is None:
            raise RuntimeError(
                "You try a send auth token, but not bound MaxApi instance to mapper"
            )

        self.max_api.id = auth_model.profile.contact.id
        self.max_api.me = cast(Profile, translate_models(auth_model.profile))
        self.max_api.phone = str(auth_model.profile.contact.phone)
        self.max_api.chats = [
            cast(Chat, translate_models(chat)) for chat in auth_model.chats
        ]
        self.max_api.contacts = [
            cast(Contact, translate_models(contact))
            for contact in auth_model.contacts
            if contact is not None
        ]
        self.max_api.messages = {
            i: [cast(Message, translate_models(msg)) for msg in msg_list]
            for i, msg_list in auth_model.messages.items()
        }
        self.max_api.users[self.max_api.me.contact.id] = self.max_api.me.contact

        self.max_api.names = self.max_api.me.contact.names

    async def request_code(
        self,
        phone: str,
        auth_type: str = "START_AUTH",
        use_mobile_fingerprint: bool = True,
    ) -> StartSMSAuthResponse:
        user_agent = self.user_agent
        if (
            use_mobile_fingerprint
            and user_agent is not None
            and self.calls_seed is not None
            and hasattr(user_agent, "arch")
            and hasattr(user_agent, "app_version")
        ):
            mode = self.fingerprint_generator.generate_fingerprint(
                version=user_agent.app_version,
                device_id=user_agent.device_id,
                calls_seed=self.calls_seed,
                arch=user_agent.arch,
            )
        else:
            mode = None
        self._logger.info("requesting sms code phone_set=%s", bool(phone))
        response = await self.send_raw(
            method=StartSMSAuthMethod(
                phone=self.phone,
                type=auth_type,
                mode=mode,
            ),
            check_errors=True,
        )
        auth_response = StartSMSAuthResponse(**response.payload)
        return auth_response

    async def send_code(
        self,
        token: str,
        verify_code: str,
        auth_token_type: str = "CHECK_CODE",
    ) -> ChoiceLoginVariantResponse:
        check_response = await self.send_raw(
            method=VerifySMSCodeMethod(
                temp_token=token,
                auth_token_type=auth_token_type,
                verify_code=str(verify_code),
            ),
            check_errors=True,
        )
        choice = ChoiceLoginVariantResponse(payload=check_response.payload)
        return choice

    async def request_qr(
        self,
    ) -> MetadataResponse:
        response = await self.send_raw(
            method=GetMetadataForLoginMethod(), check_errors=True
        )
        metadata = MetadataResponse(**response.payload)

        return metadata

    async def check_qr(self, track_id: str) -> TrackLoginResponse:
        response = await self.send_raw_with_running_wait(
            method=TrackLoginMethod(track_id=track_id),
            # return_exception=True
        )

        track_data = TrackLoginResponse(**response.payload)

        if track_data is None:
            raise RuntimeError("Track login failed.")

        return track_data

    async def confirm_qr(self, track_id: str) -> ChoiceLoginVariantResponse:
        response = await self.send_raw_with_running_wait(
            method=GetUserDataMethod(track_id=track_id),
        )
        payload = response.payload
        user = ChoiceLoginVariantResponse(
            payload=payload,
        )
        return user

    async def confirm_registration(
        self,
        first_name: str,
        last_name: str | None,
        token: str,
    ) -> ConfirmRegistrationResponse:
        response = await self.send(
            method=ConfirmRegistrationMethod(
                first_name=first_name,
                last_name=last_name,
                token=token,
            )
        )

        return ConfirmRegistrationResponse(**response.payload)

    async def _get_track_id(self) -> str | None:
        response = await self.send(method=GetTrackIdFor2FAMethod())

        track_id = GetTrackIdFor2FAResponse(**response.payload).track_id
        return track_id

    async def _set_email(
        self,
        track_id: str,
        email: str,
        email_code_getter: Callable[[str], Coroutine[Any, Any, str]],
    ) -> None:
        response = await self.send(
            method=GetEmailCodeMethod(
                track_id=track_id,
                email=email,
            )
        )

        code = await email_code_getter(email)

        response = await self.send(
            method=VerifyEmailMethod(
                track_id=track_id,
                verify_code=code,
            )
        )

    async def _set_hint(
        self,
        track_id: str,
        hint: str,
    ) -> None:
        response = await self.send(
            method=SetHintMethod(
                track_id=track_id,
                hint=hint,
            )
        )

    async def _set_password(
        self,
        track_id: str,
        password: str,
    ) -> None:
        response = await self.send(
            method=SetPasswordMethod(
                track_id=track_id,
                password=password,
            )
        )

    async def set_2fa(
        self,
        password: str,
        email: str | None = None,
        hint: str | None = None,
        email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        if two_factor_actions is None:
            two_factor_actions = []
        track_id = await self._get_track_id()

        if track_id is None:
            raise MapperApiError("No track id provided.")

        await self._set_password(
            track_id=track_id,
            password=password,
        )

        has_hint = False
        has_email = False

        if email is not None:

            async def default_email_code_getter(e: str) -> str:
                return await asyncio.to_thread(input, f"Введите код с почты {e}: ")

            callback = email_code_getter or default_email_code_getter

            await self._set_email(
                track_id=track_id, email=email, email_code_getter=callback
            )

            has_email = True

        if hint is not None:
            await self._set_hint(track_id=track_id, hint=str(hint))
            has_hint = True

        expected_capabilities = [TwoFactorAction.SET_PASSWORD]

        if has_hint:
            if TwoFactorAction.HINT not in expected_capabilities:
                expected_capabilities.append(TwoFactorAction.HINT)
        if has_email:
            if TwoFactorAction.EMAIL not in expected_capabilities:
                expected_capabilities.append(TwoFactorAction.EMAIL)

        response = await self.send(
            method=SetTwoFactorMethod(
                track_id=track_id,
                password=password,
                hint=str(hint) if has_hint else None,
                expected_capabilities=[
                    reverse_translate_two_factor_actions(action)
                    for action in expected_capabilities
                ],
            )
        )

    async def _check_2fa_password(
        self, track_id: str, password: str
    ) -> GetTrackIdFor2FAResponse:
        response = await self.send(
            method=CheckPasswordMethod(
                track_id=track_id,
                password=password,
            )
        )

        return GetTrackIdFor2FAResponse(**response.payload)

    async def remove_2fa(
        self,
        password: str,
        expected_capabilities: list[TwoFactorAction] | None = None,
        remove_2fa: bool = True,
    ) -> None:
        if expected_capabilities is None:
            expected_capabilities = []
        self._logger.info("removing 2fa password_set=%s", bool(password))

        track_id = await self._get_track_id()

        if track_id is None:
            self._logger.error("missing track_id in auth create track response")
            raise RuntimeError("Failed to create auth track")

        await self._check_2fa_password(track_id, password)

        response = await self.send(
            method=RemoveTwoFactorMethod(
                track_id=track_id,
                expected_capabilities=[
                    reverse_translate_two_factor_actions(action)
                    for action in expected_capabilities
                ],
                remove2fa=remove_2fa,
            )
        )
        return None

    async def approve_qr_login(self, qr_link: str) -> None:
        response = await self.send(
            method=ApproveQrLoginMethod(
                qr_link=qr_link,
            )
        )
        return None

    async def check_2fa(self) -> bool:
        if self.max_api is None:
            raise RuntimeError("Mapper not bound to MaxApi instance.")

        if self.max_api.me is None or self.max_api.me.profile_options is None:
            return False
        return (
            ProfileOptionsMappingModel.SECOND_FACTOR_PASSWORD_ENABLED
            in self.max_api.me.profile_options
        )

    async def change_password(
        self,
        password_old: str,
        password_new: str,
        expected_capabilities: list[TwoFactorAction] | None = None,
        hint: str | None = None,
    ) -> None:
        if expected_capabilities is None:
            expected_capabilities = []
        if TwoFactorAction.UPDATE_PASSWORD not in expected_capabilities:
            expected_capabilities.append(TwoFactorAction.UPDATE_PASSWORD)

        track_id = await self._get_track_id()

        if not track_id:
            self._logger.error("missing track_id in auth create track response")
            raise RuntimeError("Failed to create auth track")

        await self._check_2fa_password(track_id, password_old)

        await self._set_password(track_id, password_new)

        response = await self.send(
            method=SetTwoFactorMethod(
                track_id=track_id,
                password=password_new,
                hint=hint,
                expected_capabilities=[
                    reverse_translate_two_factor_actions(action)
                    for action in expected_capabilities
                ],
            )
        )

    async def login(
        self,
        url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
        login_backoff: Backoff | None = None,
        registration_config: RegistrationConfig | None = None,
        use_mobile_fingerprint: bool = True,
    ) -> SuccessLoginResponse | None:

        token = self.token

        if token is None:

            self._logger.info("haven`t token. Start login...")
            if self.user_agent is None:
                raise RuntimeError("user agent is not initialized.")
            user = await self._login(
                user_agent=self.user_agent,
                login_backoff=login_backoff,
                url_callback=url_callback,
                registration_config=registration_config,
                use_mobile_fingerprint=use_mobile_fingerprint,
            )

            self._logger.info("get token from login...")

            token = user.token_attrs.token
            self.token: str | None = token

            if token is None:
                raise MapperApiError("Server not return token.")

            await write_token(token=token, name_of_token=self.TOKEN_NAME)
            self._logger.info("was write token in tokens.json successfully.")
            return user
        else:
            self._logger.info("token was get from tokens.json")
            self.token = token
            return None

    async def _login(
        self,
        user_agent: BaseUserAgentMappingModel,
        login_backoff: Backoff | None = None,
        code_getter: Callable[[str], Coroutine[Any, Any, int]] | None = None,
        url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
        registration_config: RegistrationConfig | None = None,
        use_mobile_fingerprint: bool = True,
    ) -> SuccessLoginResponse:
        if login_backoff is None:
            login_backoff = Backoff(config=DEFAULT_BACKOFF_CONFIG)
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

        try:
            await self._send_user_agent(
                user_agent=user_agent,
            )

            choice: ChoiceLoginVariantResponse = await self._call_build_in_method(
                method_name="LOGIN",
                # metadata=metadata,
                url_callback=url_callback,
                code_getter=code_getter,
                login_backoff=login_backoff,
                user_agent=user_agent,
                sms_auth=self.sms_auth,
                registration_config=registration_config,
                use_mobile_fingerprint=use_mobile_fingerprint,
            )
            user: SuccessLoginResponse

            if isinstance(choice.payload, TwoFactorLoginResponse):
                if self.password is None:
                    raise MapperApiError(
                        "password is required to login in account with 2FA."
                    )
                user = await self.resolve_two_factor(
                    track_id=choice.payload.password_challenge.track_id,
                    password=self.password,
                )
            else:
                user = choice.payload

            return user
        except MapperCancelledError:
            self._logger.error("Login cancelled")
            await login_backoff.asleep()
            raise RestartMapperError("Failed to login")
        except TimeoutError as e:
            self._logger.error("Login timed out")
            raise RestartMapperError("Failed to login - timeout")
        except Exception as e:
            self._logger.error("Failed to login: %s - %s", e.__class__.__name__, e)
            await login_backoff.asleep()
            raise RestartMapperError("Failed to login")

    async def resolve_two_factor(
        self, track_id: str, password: str
    ) -> SuccessLoginResponse:
        # if password is None:
        #     raise RuntimeError("No password given, but need 2FA")
        response = await self.send_raw_with_running_wait(
            method=Resolve2FAMethod(
                password=password,
                track_id=track_id,
            )
        )
        user = SuccessLoginResponse(**response.payload)
        return user

    async def _auth(
        self,
        token: str,
        user_agent: BaseUserAgentMappingModel,
        chats_count: int = 40,
        interactive: bool = True,
        presence_sync: int = -1,
        chats_sync: int = 0,
        contacts_sync: int = 0,
        drafts_sync: int = 0,
        send_user_agent: bool = True,
    ) -> None:
        try:
            if send_user_agent:
                await self._send_user_agent(
                    user_agent=user_agent,
                )

            await self._send_auth_token(
                token=token,
                chats_count=chats_count,
                interactive=interactive,
                presence_sync=presence_sync,
                chats_sync=chats_sync,
                contacts_sync=contacts_sync,
                drafts_sync=drafts_sync,
            )
            self._authorized.set()
        except BaseMapperError as e:
            self._logger.warning("Cancelled auth")
            self._authorized.clear()
            raise RestartMapperError("Auth failed") from e
        except Exception as e:
            self._logger.warning("Unexpected error while auth: %s", e)
            self._authorized.clear()
            raise RestartMapperError("Auth failed") from e

    async def _keepalive(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._keepalive_ping_interval)
                self._logger.debug("send keepalive ping...")
                pong = await self.send(
                    method=SendKeepAlivePingMethod(
                        interactive=self.keep_alive_interactive
                    ),
                    return_exception=True,
                )
                self._logger.debug("keepalive pong %s", pong)
        except MapperCancelledError:
            self._logger.warning("keepalive ping canceled")
        except MapperTransportError as e:
            self._logger.warning("keepalive transport error: %s", e, exc_info=True)
