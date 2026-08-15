import asyncio
import logging
import json
from typing import Any, cast
from xmlrpc.client import Binary


import websockets
from websockets import Origin
from websockets.asyncio.client import ClientConnection, connect

from .bases import StreamTransport
from .registry import register_transport
from ..config import DEFAULT_WEB_HEADER_USER_AGENT
from ..encoding import BaseEncoding
from ..exceptions import BaseTransportError, ConnectTransportError, ConnectionTransportError, SendingTransportError

# Just aliases

# WebSocketClosedException = websockets.ConnectionClosed
# WebSocketException = websockets.WebSocketException


@register_transport("websocket")
class WebSocketTransport(StreamTransport[BaseEncoding[Any, Any, Any, Any]]):
    # BASE_EXCEPTION_FOR_TRANSPORT = WebSocketException
    # OTHER_EXCEPTIONS_FOR_TRANSPORT = [WebSocketClosedException]

    def __init__(
        self,
        encoding: BaseEncoding[Any, Any, Any, Any],
        *args: Any,
        url: str = "wss://ws-api.oneme.ru/websocket",
        proxy: str | None = None,
        origin: str = "https://web.max.ru",
        user_agent_header: str = DEFAULT_WEB_HEADER_USER_AGENT,
        **kwargs: Any,
    ) -> None:
        """Initialize the web socket transport.

        :param url: Resource URL.
        :type url: str
        :param origin: The origin value.
        :type origin: str
        :param user_agent_header: The user agent header value.
        :type user_agent_header: str
        """
        self._encoding = encoding

        self.url = url
        self.proxy = proxy
        self.origin = Origin(origin)
        self.user_agent_header = user_agent_header
        self.ws: ClientConnection | None = None
        self.__logger = logging.getLogger("WebSocketTransport")

    async def _async_init(
        self,
        encoding: BaseEncoding[Any, Any, Any, Any],
        proxy: str | None = None,
        *args: Any,
        url: str = "wss://ws-api.oneme.ru/websocket",
        **kwargs: Any,
    ) -> None:
        """Async init.

        :param url: Resource URL.
        :type url: str
        """
        await asyncio.to_thread(self.__init__, url=url, encoding=encoding, proxy=proxy,)  # type: ignore[misc]
        self.__logger.info("Initializing WebSocket Transport")

        self.__logger.info("WebSocket was initialized")
        await self.connect()
        self.__logger.info("WebSocket connected to %s", self.url)

    async def connect(self, **kwargs: Any) -> None:
        """Connect.

        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :raises ConnectTransportError: If connection handshake timed out or handle unknown error.
        """
        if self.ws:
            self.__logger.info("WebSocket already connected to %s", self.url)
            await self.close()
            self.__logger.info("WebSocket was close")
        self.__logger.info("Connecting to %s", self.url)
        try:
            if self.proxy:
                self.ws = await connect(
                    self.url,
                    origin=self.origin,
                    proxy=self.proxy,
                )
            else:
                self.ws = await connect(
                    self.url,
                    origin=self.origin,
                    user_agent_header=self.user_agent_header,
                    # ping_interval=1,
                    # ping_timeout=0.01,
                    # just a for tests
                )
        except asyncio.TimeoutError as e:
            self.__logger.warning("Websocket url=%s connection handshake timed out", self.url)
            raise ConnectTransportError("Websocket connection handshake timed out") from e
        except Exception as e:
            self.__logger.error("Handler unknown exception while connecting to websocket url=%s: %s",self.url, e)
            raise ConnectTransportError("Websocket connection unknown exception") from e
        self.__logger.info("WebSocket connected to %s", self.url)

    async def close(self) -> None:
        """Close."""
        if self.ws is not None:
            ws = self.ws
            await ws.close()
            await ws.wait_closed()
            self.ws = None
            self.__logger.info("Websocket closed")
        else:
            self.__logger.info("Websocket already closed")

    async def send(self, data: Binary | str | bytes | dict[str, Any]) -> None:
        """Send.

        :param data: Contextual data passed through the processing pipeline.
        :type data: Binary | str | bytes | dict[str, Any]
        :raises TypeError: If data must be str or bytes.
        :raises SendingTransportError: If you try to send before initialization connection.
        """
        if not isinstance(data, (Binary, str, bytes, dict)):
            raise TypeError("data must be str or bytes")

        if self.ws is None:
            raise SendingTransportError("You try to send before initialization connection")

        if not self.connected:
            raise SendingTransportError("You try to send before initialization connection")

        self.__logger.debug("Sending data: %s", data)
        await self.ws.send(cast(bytes, data))

    async def recv(self) -> Any:
        """Recv.

        :returns: The value returned by backend.
        :rtype: Any
        :raises ConnectionTransportError: If you try to recv before initialization connection.
        """
        if self.ws is None or not self.connected:
            raise ConnectionTransportError("You try to recv before initialization connection")
        response = await self.ws.recv()
        return response

    # @property
    # def connected(self) -> bool:
    #     return self.ws is not None

    @property
    def connected(self) -> bool:
        return bool(self.ws and self.ws.close_code is None)
