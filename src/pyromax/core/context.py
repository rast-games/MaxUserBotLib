from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast


from ..mixins import AsyncConstructorType

from ..protocol.registry import PROTOCOLS as _PROTOCOLS
from ..transport.registry import TRANSPORTS as _TRANSPORTS
from ..mapping.registry import MAPPERS as _MAPPERS
from ..encoding.registry import ENCODINGS as _ENCODINGS

from ..protocol import BaseMaxProtocol
from ..transport import BaseTransport
from ..mapping import BaseMapper
from ..encoding import BaseEncoding

PROTOCOLS = cast(dict[str, AsyncConstructorType[BaseMaxProtocol[Any, Any]]], _PROTOCOLS)
TRANSPORTS = cast(dict[str, AsyncConstructorType[BaseTransport[Any]]], _TRANSPORTS)
MAPPERS = cast(dict[str, AsyncConstructorType[BaseMapper[Any, Any]]], _MAPPERS)
ENCODINGS = _ENCODINGS
