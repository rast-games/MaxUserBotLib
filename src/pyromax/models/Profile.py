from .base import BaseMaxObject
from .Contact import Contact


class Profile(BaseMaxObject):
    contact: Contact
    profile_options: list[int] | None
