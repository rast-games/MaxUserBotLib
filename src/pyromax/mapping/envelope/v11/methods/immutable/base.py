import abc
from typing import Any


from ......protocol import Envelope, BaseMaxProtocolMethod
from ....constants import Opcode, Cmd
from ...constants import VERSION


class BaseMethod(abc.ABC, BaseMaxProtocolMethod[Envelope]):
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the base method.

        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        """
        self.args = kwargs

    @abc.abstractmethod
    async def __call__(self, request: Envelope) -> Envelope:
        """Populate an envelope for the base protocol request.

        :param request: Protocol request envelope to populate or send.
        :type request: Envelope
        :returns: The envelope populated with the request opcode and payload.
        :rtype: Envelope
        """
        pass


__all__ = [
    "BaseMethod",
    "Opcode",
    "Cmd",
    "VERSION",
    "Envelope",
]
