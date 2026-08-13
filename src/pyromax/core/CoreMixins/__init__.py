from typing import Protocol

from ...mixins import AsyncConstructorMeta
from .Auth import AuthMixin
from .Chat import ChatMixin
from .User import UserMixin
from .File import FileMixin
from .Contacts import ContactsMixin
from .Message import MessageMixin


class AsyncConstructorProtocolMeta(type(Protocol), AsyncConstructorMeta):  # type: ignore[misc]
    pass


class FullMixin(
    AuthMixin,
    MessageMixin,
    ChatMixin,
    UserMixin,
    FileMixin,
    ContactsMixin,
):
    pass


__all__ = [
    "FullMixin",
    "AsyncConstructorProtocolMeta",
]
