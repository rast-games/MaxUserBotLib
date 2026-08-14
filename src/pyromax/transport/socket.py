import asyncio
import logging
import random
import struct
from typing import Any, cast, Final
import ssl
import json
from socket import gaierror

import lz4.block  # type: ignore[import-untyped]
import msgpack  # type: ignore[import-untyped]


from .bases import StreamTransport
from .registry import register_transport
from ..exceptions import (
    SocketTransportError,
    SocketTransportConnectionError,
    SocketTransportSendError,
)
from ..encoding import SocketEncoding


@register_transport("socket")
class SocketTransport(StreamTransport[SocketEncoding[Any, Any]]):

    BASE_EXCEPTION_FOR_TRANSPORT = SocketTransportError
    OTHER_EXCEPTIONS_FOR_TRANSPORT = [
        SocketTransportConnectionError,
        SocketTransportSendError,
    ]

    __reader: asyncio.StreamReader | None
    __writer: asyncio.StreamWriter | None
    __buffer: bytearray
    __logger: logging.Logger
    _ssl_context: ssl.SSLContext
    url: str
    port: int

    async def _async_init(
        self,
        encoding: SocketEncoding[Any, Any],
        *args: Any,
        url: str = "api.oneme.ru",
        host: str = "api.oneme.ru",
        port: int = 443,
        **kwargs: Any,
    ) -> None:
        """Async init.

        :param url: Resource URL.
        :type url: str
        :param host: The host value.
        :type host: str
        :param port: The port value.
        :type port: int
        """
        self._encoding = encoding

        self.url = url
        self.port = port
        self.__buffer = bytearray()
        self.__logger = logging.getLogger("SocketTransport")
        await asyncio.to_thread(self.__init__, encoding=encoding,)  # type: ignore[misc]
        while True:
            try:
                self.__reader, self.__writer = await asyncio.open_connection(
                    self.url, self.port, ssl=self._ssl_context
                )
                break
            except ConnectionError as e:
                self.__logger.error("Connection error: %s", e)
                await asyncio.sleep(1)
            except gaierror as e:
                self.__logger.error("Gaierror: %s", e)
                await asyncio.sleep(2)

    def __init__(
        self,
        encoding: SocketEncoding[Any, Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the socket transport."""
        self._encoding = encoding
        self.__reader = None
        self.__writer = None
        self._ssl_context = ssl.create_default_context()

    async def send(self, request: bytes) -> None:
        """Send.

        :param request: Protocol request envelope to populate or send.
        :type request: bytes
        """
        assert self.__writer is not None, "Writer is not initialized"
        self.__writer.write(request)
        await self.__writer.drain()

    async def _recv_raw(self, nbytes: int) -> bytes:
        """Recv raw.

        :param nbytes: The nbytes value.
        :type nbytes: int
        :returns: The resulting bytes value.
        :rtype: bytes
        :raises SocketTransportConnectionError: If graceful shutdown.
        :raises SocketTransportConnectionError: If the requested action cannot be completed.
        """
        assert self.__reader is not None, "Reader is not initialized"

        loop = asyncio.get_running_loop()
        try:
            while len(self.__buffer) < nbytes:
                chunk = await self.__reader.readexactly(nbytes - len(self.__buffer))
                if chunk == b"":
                    self.__buffer.clear()
                    await self.close()
                    self.__logger.info("Server close connection with graceful shutdown")
                    raise SocketTransportConnectionError("graceful shutdown")
                self.__buffer.extend(chunk)
            result = self.__buffer[:nbytes]
            self.__buffer = self.__buffer[nbytes:]
            return bytes(result)
        except asyncio.IncompleteReadError as e:
            self.__buffer.clear()
            await self.close()
            self.__logger.info("Server close connection with graceful shutdown")
            raise SocketTransportConnectionError("graceful shutdown")
        except (ConnectionResetError, BrokenPipeError) as e:
            self.__logger.error("Socket connection broken: %s", e)
            await self.close()
            self.__buffer.clear()
            raise SocketTransportConnectionError(f"Connection broken: {e}")
        except Exception as e:
            self.__buffer = bytearray()
            await self.close()
            self.__logger.error("Socket recv error: %s", e)
            raise SocketTransportConnectionError(f"Socket recv error: {e}")

    async def recv(self) -> Any:
        """Recv.

        :returns: The value returned by backend.
        :rtype: Any
        :raises SocketTransportError: If uncompressed return None.
        :raises SocketTransportError: If the requested action cannot be completed.
        """
        loop = asyncio.get_running_loop()

        header_raw = await self._recv_raw(self._encoding.HEADER_SIZE)
        payload_length = self._encoding.unpack_header_to_get_payload_length(header_raw)
        # ver, cmd, seq, opcode, cof, payload_len = struct.unpack(">BBHHB3s", header_raw)
        # payload_length = int.from_bytes(payload_len, "big")
        if payload_length > 0:
            payload_raw = await self._recv_raw(payload_length)
        else:
            payload_raw = b""

        return header_raw + payload_raw

    async def connect(self, **kwargs: Any) -> None:
        """Connect.

        # :param kwargs: Keyword arguments forwarded to the wrapped callable.
        # :type kwargs: Any
        :raises SocketTransportConnectionError: If the requested action cannot be completed.
        """
        try:

            self.__reader, self.__writer = await asyncio.open_connection(
                self.url, self.port, ssl=self._ssl_context
            )
        except Exception as e:
            self.__logger.error("Socket connection error: %s", e)
            raise SocketTransportConnectionError(f"Socket connection error: {e}") from e
        self.__logger.info("Socket connected")

    async def close(self) -> None:
        """Close."""
        if self.__writer:
            try:
                self.__writer.close()
                await self.__writer.wait_closed()
            except Exception as e:
                self.__logger.error(f"Error while closing socket: {e}")
            finally:
                self.__writer = None
                self.__reader = None
                self.__buffer.clear()
        self.__logger.info("Socket closed")

    @property
    def connected(self) -> bool:
        return self.__writer is not None
