from collections.abc import Sequence
from typing import cast

from ...methods import (
    GetMembersByIdsMethod,
    GetUsersMethod,
    SearchByPhoneMethod,
    GetSessionsMethod,
    GetChatIdMethod,
    AddContactMethod,
    RemoveContactMethod,
    ImportContactsMethod,
)
from ...models import (
    Contact,
    Session,
    ContactInfo,
)
from .CoreMixinsProtocol import CoreMixinsProtocol


class ContactsMixin(CoreMixinsProtocol):
    async def get_members_by_ids(self, member_ids: list[int]) -> Sequence[Contact]:
        """Retrieve members by ids.

        :param member_ids: Identifiers of the members.
        :type member_ids: list[int]
        :returns: The Contacts collection.
        :rtype: Sequence[Contact]
        """

        contacts = cast(
            Sequence[Contact],
            await self(
                GetMembersByIdsMethod,
                member_ids=member_ids,
            ),
        )
        return contacts
        # return await self.mapper.get_member_by_id(member_id)

    async def get_member_by_id(self, member_id: int) -> Contact | None:
        """Retrieve member by id.

        :param member_id: Identifier of the member.
        :type member_id: int
        :returns: The resulting Contact | None.
        :rtype: Contact | None
        """
        contacts = await self.get_members_by_ids(member_ids=[member_id])
        return contacts[0] if contacts else None

    async def get_users(self, user_ids: list[int]) -> list[Contact]:
        """Retrieve users.

        :param user_ids: Identifiers of the users.
        :type user_ids: list[int]
        :returns: The resulting collection.
        :rtype: list[Contact]
        """

        user = cast(
            list[Contact],
            await self(
                GetUsersMethod,
                user_ids=user_ids,
            ),
        )
        return user

    async def get_user(self, user_id: int) -> Contact | None:
        """Retrieve user.

        :param user_id: Identifier of the user.
        :type user_id: int
        :returns: The resulting Contact | None.
        :rtype: Contact | None
        """
        user = await self.get_users(user_ids=[user_id])
        return user[0] if user else None

    async def search_by_phone(self, phone: str) -> Contact:
        """Search for by phone.

        :param phone: Phone number in the format accepted by MAX.
        :type phone: str
        :returns: The resulting Contact.
        :rtype: Contact
        """

        user = cast(
            Contact,
            await self(
                SearchByPhoneMethod,
                phone=phone,
            ),
        )
        return user

    async def get_sessions(self) -> list[Session]:
        """Retrieve sessions.

        :returns: The Sessions collection.
        :rtype: list[Session]
        """

        return cast(list[Session], await self(GetSessionsMethod))

    async def get_chat_id(self, first_user_id: int, second_user_id: int) -> int:
        """Retrieve chat id.

        :param first_user_id: Identifier of the first user.
        :type first_user_id: int
        :param second_user_id: Identifier of the second user.
        :type second_user_id: int
        :returns: The resulting int value.
        :rtype: int
        """
        return cast(
            int,
            await self(
                GetChatIdMethod,
                first_user_id=first_user_id,
                second_user_id=second_user_id,
            ),
        )

    async def add_contact(self, contact_id: int) -> Contact:
        """Add contact.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        :returns: The resulting Contact.
        :rtype: Contact
        """

        return cast(
            Contact,
            await self(
                AddContactMethod,
                contact_id=contact_id,
            ),
        )

    async def remove_contact(self, contact_id: int) -> None:
        """Remove contact.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        """
        return cast(
            None,
            await self(
                RemoveContactMethod,
                contact_id=contact_id,
            ),
        )

    async def import_contacts(self, contacts: list[ContactInfo]) -> list[Contact]:
        """Import contacts.

        :param contacts: Collection of contacts.
        :type contacts: list[ContactInfo]
        :returns: The Contacts collection.
        :rtype: list[Contact]
        """

        return cast(
            list[Contact],
            await self(
                ImportContactsMethod,
                contacts=contacts,
            ),
        )
