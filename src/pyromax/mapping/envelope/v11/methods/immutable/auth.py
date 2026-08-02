from .base import BaseMethod, Envelope, Opcode, Cmd
from ...payloads.models import (
    TrackLoginMappingModel,
    AuthMappingModel,
    BaseUserAgentMappingModel,
)
from ...payloads.requests import (
    KeepAliveRequest,
    Resolve2FARequest,
    StartPhoneAuthRequest,
    VerifySMSCodeRequest,
    ConfirmRegistrationRequest,
    GetEmailCodeRequest,
    SetHintRequest,
    SetPasswordRequest,
    VerifyEmailRequest,
    GetTrackIdFor2FARequest,
    SetTwoFactorRequest,
)
from .base import VERSION


class TrackLoginMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.TRACK_LOGIN
        request.cmd = Cmd.REQUEST
        request.payload = TrackLoginMappingModel(
            track_id=self.args["track_id"],
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION

        return request


class GetUserDataMethod(TrackLoginMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request = await super().__call__(request)
        request.opcode = Opcode.GET_USER_DATA
        request.ver = VERSION
        return request


class Resolve2FAMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.RESOLVE_2FA
        request.cmd = Cmd.REQUEST
        request.payload = Resolve2FARequest(
            track_id=self.args["track_id"],
            password=self.args["password"],
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION
        return request


class StartSMSAuthMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.START_SMS_AUTH
        request.cmd = Cmd.REQUEST
        request.payload = StartPhoneAuthRequest(
            type=self.args["type"],
            phone=self.args["phone"],
            mode=self.args.get("mode"),
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION
        return request


class VerifySMSCodeMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.CHECK_SMS_CODE
        request.cmd = Cmd.REQUEST
        request.payload = VerifySMSCodeRequest(
            auth_token_type=self.args["auth_token_type"],
            token=self.args["temp_token"],
            verify_code=self.args["verify_code"],
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION
        return request


class GetMetadataForLoginMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.METADATA_FOR_LOGIN
        request.cmd = Cmd.REQUEST
        request.payload = None
        request.ver = VERSION
        return request


class SendUserAgentMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SEND_USER_AGENT
        request.cmd = Cmd.REQUEST
        user_agent: BaseUserAgentMappingModel = self.args["user_agent"]
        request.payload = user_agent.to_request().model_dump(
            by_alias=True, exclude_none=True
        )
        request.ver = VERSION
        return request


class SendAuthTokenMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.AUTHORIZE
        request.cmd = Cmd.REQUEST
        request.payload = AuthMappingModel(**self.args).model_dump(
            by_alias=True, exclude_none=True
        )
        request.ver = VERSION
        return request


class SendKeepAlivePingMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.PING
        request.cmd = Cmd.REQUEST
        request.payload = KeepAliveRequest(
            interactive=self.args.get("interactive", True),
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION
        return request


class ConfirmRegistrationMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.CONFIRM_REGISTRATION
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ConfirmRegistrationRequest(
            token=self.args["token"],
            first_name=self.args["first_name"],
            last_name=self.args["last_name"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetEmailCodeMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SET_EMAIL
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetEmailCodeRequest(
            track_id=self.args["track_id"],
            email=self.args["email"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class VerifyEmailMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.VERIFY_EMAIL
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = VerifyEmailRequest(
            track_id=self.args["track_id"],
            verify_code=self.args["verify_code"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class SetHintMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SET_HINT
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = SetHintRequest(
            track_id=self.args["track_id"],
            hint=self.args["hint"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class SetPasswordMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SET_PASSWORD
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = SetPasswordRequest(
            track_id=self.args["track_id"],
            password=self.args["password"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetTrackIdFor2FAMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_TRACKID_FOR2FA
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetTrackIdFor2FARequest().model_dump(
            by_alias=True, exclude_none=True
        )
        return request


class SetTwoFactorMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SET_2_FACTOR
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = SetTwoFactorRequest(
            expected_capabilities=self.args["expected_capabilities"],
            track_id=self.args["track_id"],
            password=self.args["password"],
            hint=self.args.get("hint"),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    "TrackLoginMethod",
    "GetUserDataMethod",
    "Resolve2FAMethod",
    "StartSMSAuthMethod",
    "VerifySMSCodeMethod",
    "GetMetadataForLoginMethod",
    "SendUserAgentMethod",
    "SendAuthTokenMethod",
    "SendKeepAlivePingMethod",
    "ConfirmRegistrationMethod",
    "GetEmailCodeMethod",
    "SetHintMethod",
    "SetPasswordMethod",
    "VerifyEmailMethod",
    "GetTrackIdFor2FAMethod",
    "SetTwoFactorMethod",
]
