from .base import BaseMaxObject


class RegistrationConfig(BaseMaxObject):
    first_name: str
    last_name: str | None = None
