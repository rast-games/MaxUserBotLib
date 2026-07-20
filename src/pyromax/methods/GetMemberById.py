from collections.abc import Sequence

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact


class GetMemberByIdMethod(BaseMaxApiMethod[Sequence[Contact]]):
    async def __call__(
            self,
            member_id: int,
    ) -> Sequence[Contact]:
        if not self._max_api:
            raise RuntimeError('GetMemberByIdMethod method not bound to MaxApi instance')
        contacts = await self._max_api.mapper.get_member_by_id(
            member_id=member_id,
        )
        # contacts = await self._max_api.mapper.call_method(
        #     type(self),
        #     member_id=member_id
        # )
        return contacts

