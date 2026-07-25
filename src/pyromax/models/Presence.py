from .base import BaseMaxObject


class Presence(BaseMaxObject):
    seen: int | None = None
    status: int | None = None