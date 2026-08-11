from .base import BaseMaxObject
from .Contact import Contact
from .Presence import Presence


class Member(BaseMaxObject):
    contact: Contact
    presence: Presence
