from collections.abc import Sequence

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact


class GetMemberByIdMethod(BaseMaxApiMethod[Contact]):
    async def __call__(
            self,
            member_id: int,
    ) -> Sequence[Contact]:
        if not self._max_api:
            raise RuntimeError('GetMemberByIdMethod method not bound to MaxApi instance')
        contacts = await self._max_api.mapper.get_member_by_id(
            member_id=member_id,
        )
        return contacts

