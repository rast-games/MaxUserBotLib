from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .bases import BaseTransport

if TYPE_CHECKING:
    from ..mixins import AsyncConstructorType

TRANSPORTS = {}


def register_transport(
    transport: str,
) -> Callable[[type[BaseTransport]], type[BaseTransport]]:
    """Register transport.

    :param transport: name of the transport.
    :type transport: str
    :returns: The decorator Callable[[type[BaseTransport]], type[BaseTransport]].
    :rtype: Callable[[type[BaseTransport]], type[BaseTransport]]
    """
    global TRANSPORTS

    def wrapper(cls: type[BaseTransport]) -> type[BaseTransport]:
        """Wrapper.

        :param cls: transport class
        :type cls: type[BaseTransport]
        :returns: The resulting type[BaseTransport].
        :rtype: type[BaseTransport]
        """
        TRANSPORTS[transport] = cls
        return cls

    return wrapper
