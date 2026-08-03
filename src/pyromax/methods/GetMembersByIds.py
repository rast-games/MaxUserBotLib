from collections.abc import Sequence

from .Base import BaseMaxApiMethod
from ..models.Contact import Contact


class GetMembersByIdsMethod(BaseMaxApiMethod[Sequence[Contact]]):
    async def __call__(
        self,
        member_ids: list[int],
    ) -> Sequence[Contact]:
        if not self._max_api:
            raise RuntimeError(
                "GetMembersByIdsMethod method not bound to MaxApi instance"
            )
        contacts = await self._max_api.mapper.get_members_by_ids(
            member_ids=member_ids,
        )
        # contacts = await self._max_api.mapper.call_method(
        #     type(self),
        #     member_id=member_id
        # )
        return contacts
