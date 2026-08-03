from collections.abc import Sequence
from typing import cast

from .MixinProtocol import MixinProtocol
from .....models import Contact
from ..methods.immutable import (
    GetGeneralInfoAboutMemberMethod,
)
from ..payloads.responses import (
    GetContactResponse,
)
from ..translate.ToDTO import translate_models


class ContactMixin(MixinProtocol):
    def _cache_user(self, user: Contact) -> Contact:
        self.max_api.users[user.id] = user
        return user

    def get_cached_user(self, user_id: int) -> Contact | None:
        user = self.max_api.users.get(user_id)
        self._logger.debug("get_cached_user id=%s hit=%s", user_id, bool(user))
        return user

    async def get_members_by_ids(
        self, member_ids: int | list[int]
    ) -> Sequence[Contact]:
        contact_ids: list[int]
        if isinstance(member_ids, int):
            contact_ids = [member_ids]
        elif isinstance(member_ids, list):
            contact_ids = member_ids
        else:
            raise TypeError("member_id must be int or list[int]")

        response_envelope = await self.send(
            method=GetGeneralInfoAboutMemberMethod(
                contact_ids=contact_ids,
            )
        )

        response = GetContactResponse(**response_envelope.payload)

        contacts = [
            self._cache_user(cast(Contact, translate_models(mapping_contact)))
            for mapping_contact in response.contacts
        ]

        return [contact for contact in contacts if isinstance(contact, Contact)]

        # return cast(list[BaseMaxObject], contacts)

    async def get_user(self, user_id: int) -> Contact | None:
        if user := self.get_cached_user(user_id):
            return user

        users = await self.get_members_by_ids([user_id])
        return users[0] if users is not None else None
