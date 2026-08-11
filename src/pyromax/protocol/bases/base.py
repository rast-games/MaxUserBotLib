from __future__ import annotations

from abc import abstractmethod
from asyncio import Event
from collections.abc import Awaitable, Iterable
from typing import Any, TYPE_CHECKING, TypeVar, Generic

from ...mixins import AsyncInitializerMixin, AsyncConstructorMeta
from .request_response import Request, Response

if TYPE_CHECKING:
    from .methods import BaseMaxProtocolMethod
    from ...transport import BaseTransport

T = TypeVar("T", bound=Request[Any], contravariant=True)
R = TypeVar("R", bound=Response, covariant=True)


class BaseMaxProtocol(AsyncInitializerMixin, Generic[T, R]):

    @abstractmethod
    async def send(
        self, method: BaseMaxProtocolMethod[T], data: Any | None = None
    ) -> Awaitable[R]:
        """Send.

        :param method: BaseMaxProtocolMethod[T] instance to process.
        :type method: BaseMaxProtocolMethod[T]
        :param data: Contextual data passed through the processing pipeline.
        :type data: Any | None
        :returns: The resulting Awaitable[R] value.
        :rtype: Awaitable[R]
        """
        pass

    @abstractmethod
    async def get_updates(self) -> Iterable[Any]:
        """Retrieve updates.

        :returns: The resulting collection.
        :rtype: Iterable[Any]
        """
        pass

    @property
    @abstractmethod
    def transport(self) -> BaseTransport:
        """Transport.

        :returns: The resulting BaseTransport value.
        :rtype: BaseTransport
        """
        pass
