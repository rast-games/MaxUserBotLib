from __future__ import annotations
import logging
from typing import TypeVar, Any, TYPE_CHECKING

from .base import BaseSymmetricEncoding
from .registry import register_encoding

if TYPE_CHECKING:
    from ..config import ExtraConfig

NO_ENCODED = TypeVar("NO_ENCODED")


@register_encoding("NoEncoding")
class NoEncoding(BaseSymmetricEncoding[NO_ENCODED, NO_ENCODED]):
    """
    Encoding implementation, which does nothing (works as a stub and simply returns data), exists to comply with the interface.
    In fact, it was created for the websocket transport, since the library used to work with the websocket in this
    transport itself serializes and deserializes the data, and no intervention is required.
    """

    def __init__(self, extra_config: ExtraConfig) -> None:
        super().__init__(extra_config)
        self._logger = logging.getLogger("JsonEncoding")

    def encode(self, data: NO_ENCODED, *args: Any, **kwargs: Any) -> NO_ENCODED:
        return data

    def decode(self, data: NO_ENCODED, *args: Any, **kwargs: Any) -> NO_ENCODED:
        return data
