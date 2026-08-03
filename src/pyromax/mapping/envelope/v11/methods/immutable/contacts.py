from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION

from ...payloads.requests import (
    GetContactRequest,
    SearchByPhoneRequest,
)


class GetGeneralInfoAboutMemberMethod(BaseMethod):

    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_CONTACT
        request.cmd = Cmd.REQUEST
        request.payload = GetContactRequest(
            contact_ids=self.args["contact_ids"],
        ).model_dump(by_alias=True, exclude_none=True)
        request.ver = VERSION

        return request


class SearchByPhoneMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.CONTACT_INFO_BY_PHONE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = SearchByPhoneRequest(
            phone=self.args["phone"],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    "GetGeneralInfoAboutMemberMethod",
    "SearchByPhoneMethod",
]
