from typing import Any, cast
import json

from .base import BaseEncoding
from .registry import register_encoding


@register_encoding("JsonEncoding")
class JsonEncoding(
    BaseEncoding[dict[Any, Any], str, str | dict[Any, Any], dict[Any, Any]]
):
    """
    Implementation of an encoding for serializing a dictionary to Json and deserializing Json back to a dictionary.
    This encoding was developed in the same way as the NoEncoding encoding, i.e., for websocket transport.
    However, after refactoring and logic separation, websocket transport no longer automatically convert data to Json.
    This encoding solves this problem.
    """

    def encode(self, data: dict[Any, Any], *args: Any, **kwargs: Any) -> str:
        return json.dumps(data)

    def decode(
        self, data: str | dict[Any, Any], *args: Any, **kwargs: Any
    ) -> dict[Any, Any]:
        if isinstance(data, str):
            return cast(dict[Any, Any], json.loads(data))
        else:
            return data
