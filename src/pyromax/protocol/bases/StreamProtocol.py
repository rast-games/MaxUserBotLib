from abc import abstractmethod
from collections.abc import Callable
from typing import Any, Generic

from .base import BaseMaxProtocol, T, R
from ...transport import StreamTransport


class StreamMaxProtocol(BaseMaxProtocol[T, R], Generic[T, R]):

    @abstractmethod
    async def connect(self, gen: int) -> None:
        """Connect.

        :param gen: The gen value.
        :type gen: int
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close.
        """
        pass

    @property
    @abstractmethod
    def transport(self) -> StreamTransport:
        """Transport.

        :returns: The resulting StreamTransport value.
        :rtype: StreamTransport
        """
        pass
