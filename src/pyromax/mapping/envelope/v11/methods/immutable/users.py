from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION
from ...payloads.requests import GetContactRequest, ChangeProfileRequest


class GetGeneralInfoAboutMemberMethod(BaseMethod):

    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_CONTACT
        request.cmd = Cmd.REQUEST
        request.payload = GetContactRequest(
            contact_ids=self.args["contact_ids"],
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION

        return request


class ChangeProfileMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.PROFILE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = ChangeProfileRequest(
            first_name=self.args["first_name"],
            last_name=self.args.get("last_name"),
            description=self.args.get("description"),
            photo_token=self.args.get("photo_token"),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    "GetGeneralInfoAboutMemberMethod",
    "ChangeProfileMethod",
]
