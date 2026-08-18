from __future__ import annotations
from typing import Any, Generic, TYPE_CHECKING
from typing_extensions import TypeVar
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..config import ExtraConfig

ENCODE_IN_TYPE = TypeVar("ENCODE_IN_TYPE")
ENCODE_OUT_TYPE = TypeVar("ENCODE_OUT_TYPE")
DECODE_IN_TYPE = TypeVar("DECODE_IN_TYPE")
DECODE_OUT_TYPE = TypeVar("DECODE_OUT_TYPE")


class BaseEncoding(
    ABC, Generic[ENCODE_IN_TYPE, ENCODE_OUT_TYPE, DECODE_IN_TYPE, DECODE_OUT_TYPE]
):

    def __init__(self, extra_config: ExtraConfig) -> None:
        self.extra_config = extra_config

    @abstractmethod
    def encode(
        self, data: ENCODE_IN_TYPE, *args: Any, **kwargs: Any
    ) -> ENCODE_OUT_TYPE:
        """
        Encode the given data to the given encoding type.

        :param data: The data to encode.
        :type data: Any
        """

    @abstractmethod
    def decode(
        self, data: DECODE_IN_TYPE, *args: Any, **kwargs: Any
    ) -> DECODE_OUT_TYPE:
        """
        Decode the given data to the given decoded type.

        :param data: The data to decode.
        :type data: Any
        :return:
        """


ENCODED_TYPE = TypeVar("ENCODED_TYPE")
DECODED_TYPE = TypeVar("DECODED_TYPE")


class BaseSymmetricEncoding(
    BaseEncoding[
        DECODED_TYPE,
        ENCODED_TYPE,
        ENCODED_TYPE,
        DECODED_TYPE,
    ],
    Generic[
        ENCODED_TYPE,
        DECODED_TYPE,
    ],
):
    """
    a subtype of the basic encoding, for encodings that work symmetrically, i.e. they accept one type of data for
    encoding and return another, and for decoding the same data types are used, but in the opposite way, i.e. the data
    type returned from encoding is accepted, and the data type that was originally encoded is returned
    """


class SocketEncoding(BaseSymmetricEncoding[ENCODED_TYPE, DECODED_TYPE]):
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


# class JsonAndBytesEncoding(SocketEncoding[bytes, str]):
#     """
#     The specialized type was originally created to match the Envelope protocol interface,
#     since it works with Json, and therefore all subtypes of this encoding must work with
#     Json and serialize data into bytes for sending through a socket.
#     """
#
#     @abstractmethod
#     def encode(self, data: str, *args: Any, **kwargs: Any) -> bytes: ...
#
#     @abstractmethod
#     def decode(self, data: bytes, *args: Any, **kwargs: Any) -> str: ...


class DictAndBytesEncoding(SocketEncoding[bytes, dict[Any, Any]]):
    """
    Replacement of JsonAndBytesEncoding since, due to architectural changes, EnvelopeProtocol is no longer tied to Json
    and now the encoding does not need to specifically serialize data in Json.
    """
