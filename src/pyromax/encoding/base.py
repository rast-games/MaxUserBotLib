from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod

ENCODED_TYPE = TypeVar("ENCODED_TYPE")
DECODED_TYPE = TypeVar("DECODED_TYPE")


class BaseEncoding(ABC, Generic[ENCODED_TYPE, DECODED_TYPE]):

    @abstractmethod
    def encode(self, data: DECODED_TYPE, *args: Any, **kwargs: Any) -> ENCODED_TYPE:
        """
        Encode the given data to the given encoding type.

        :param data: The data to encode.
        :type data: Any
        """

    @abstractmethod
    def decode(self, data: ENCODED_TYPE, *args: Any, **kwargs: Any) -> DECODED_TYPE:
        """
        Decode the given data to the given decoded type.

        :param data: The data to decode.
        :type data: Any
        :return:
        """


class SocketEncoding(BaseEncoding[ENCODED_TYPE, DECODED_TYPE]):
    """
    Encoding for Socket transport, it is assumed that the socket transport will expect a subtype of this class, and with
    its help understand how many bytes to read from the bus. This is done to avoid mixing abstraction levels, and the
    "dumb" transport is not responsible for the message structure, but simply reads bytes from the bus. Simply put, the
    socket transport delegates the work with the message size to it.
    """

    @property
    @abstractmethod
    def HEADER_SIZE(self) -> int:
        """
        Get the minimum size to read from the bus (i.e., the header size)
        to further understand how many more bytes need to be read from the bus.

        :returns: Header size (number of bytes).
        """

    @abstractmethod
    def unpack_header_to_get_payload_length(self, data: bytes) -> int:
        """
        Unpack the bytes header, obtained using HEADER_SIZE

        :param data: bytes of header
        :type data: bytes

        :returns: the length of the remaining message(payload)
        :rtype: int
        """


class JsonAndBytesEncoding(SocketEncoding[bytes, str]):
    """
    The specialized type was originally created to match the Envelope protocol interface,
    since it works with Json, and therefore all subtypes of this encoding must work with
    Json and serialize data into bytes for sending through a socket.
    """

    @abstractmethod
    def encode(self, data: str, *args: Any, **kwargs: Any) -> bytes: ...

    @abstractmethod
    def decode(self, data: bytes, *args: Any, **kwargs: Any) -> str: ...
