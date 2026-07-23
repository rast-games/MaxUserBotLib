from .base import BaseMaxObject


class Name(BaseMaxObject):
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    type: str | None = None
