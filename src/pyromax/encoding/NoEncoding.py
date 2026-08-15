from typing import TypeVar, Any

from .base import BaseSymmetricEncoding
from .registry import register_encoding

NO_ENCODED = TypeVar("NO_ENCODED")


@register_encoding("NoEncoding")
class NoEncoding(BaseSymmetricEncoding[NO_ENCODED, NO_ENCODED]):
    """
    Encoding implementation, which does nothing (works as a stub and simply returns data), exists to comply with the interface.
    In fact, it was created for the websocket transport, since the library used to work with the websocket in this
    transport itself serializes and deserializes the data, and no intervention is required.
    """

    def encode(self, data: NO_ENCODED, *args: Any, **kwargs: Any) -> NO_ENCODED:
        return data

    def decode(self, data: NO_ENCODED, *args: Any, **kwargs: Any) -> NO_ENCODED:
        return data
