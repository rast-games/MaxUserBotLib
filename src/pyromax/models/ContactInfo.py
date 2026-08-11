from .base import BaseMaxObject


class ContactInfo(BaseMaxObject):
    phone: str
    first_name: str
    last_name: str | None = None
