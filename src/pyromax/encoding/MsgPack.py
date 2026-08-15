import json
import logging
import struct
from typing import Any, cast

import lz4.block  # type: ignore[import-untyped]
import msgpack  # type: ignore[import-untyped]

from .base import DictAndBytesEncoding
from .registry import register_encoding


@register_encoding("MsgPackDictEncoding")
class MsgPackDictEncoding(DictAndBytesEncoding):
    """
    An encoding implementation suitable for use with the Envelope protocol and socket transport determines the size of
    the socket message header and provides an implementation for obtaining the message length from the header.
    Serializes Json data into bytes and deserializes bytes into Json.
    """

    _HEADER_SIZE: int = 10

    @property
    def HEADER_SIZE(self) -> int:
        return self._HEADER_SIZE

    def encode(self, data: str | dict[Any, Any], *args: Any, **kwargs: Any) -> bytes:
        request: dict[Any, Any]
        if isinstance(data, str):
            request = json.loads(data)
        else:
            request = data

        seq = int(request.get("seq", 0))
        opcode = int(request.get("opcode", 1))
        cmd = int(request.get("cmd", 0))
        ver = int(request.get("ver", 11))
        del request["seq"]
        del request["opcode"]
        del request["cmd"]
        if "ver" in request:
            del request["ver"]
        if not ver:
            ver = 11
        packet = self._create_packet(
            seq, opcode, cmd, ver, payload=request.get("payload")
        )

        return packet

    def _unpack_header(self, data: bytes) -> tuple[int, int, int, int, int, int]:

        header_raw = data[: self.HEADER_SIZE]

        ver, cmd, seq, opcode, cof, payload_len = struct.unpack(">BBHHB3s", header_raw)
        payload_length = int.from_bytes(payload_len, "big")
        return ver, cmd, seq, opcode, cof, payload_length

    def unpack_header_to_get_payload_length(self, data: bytes) -> int:
        _, _, _, _, _, payload_len = self._unpack_header(data)
        return payload_len

    def decode(self, data: bytes, *args: Any, **kwargs: Any) -> dict[Any, Any]:
        header_raw = data[: self.HEADER_SIZE]

        ver, cmd, seq, opcode, cof, payload_length = self._unpack_header(header_raw)
        if payload_length > 0:
            payload_raw = data[10:]
            if len(payload_raw) != payload_length:
                raise ValueError("payload length does not match")
        else:
            payload_raw = b""

        payload_uncompressed: bytes
        if cof > 0 and len(payload_raw) > 0:
            try:
                decompressed = self._safe_decompress(
                    payload_raw, start_uncompressed_size=payload_length
                )
                if decompressed is None:
                    raise ValueError("Uncompressed return None")
                payload_uncompressed = decompressed

            except ValueError as e:
                raise e
            except Exception as e:
                logging.error(f"uncompressed error: {e}")
                raise ValueError(f"uncompressed error: {e}")
        else:
            payload_uncompressed = payload_raw

        if len(payload_raw) > 0:
            try:
                decoded_payload = msgpack.unpackb(
                    payload_uncompressed, strict_map_key=False
                )
            except Exception as e:
                logging.error(f"unpack error: {e}")
                raise ValueError(f"unpack error: {e}")
        else:
            decoded_payload = {}

        return {
            "opcode": opcode,
            "cmd": cmd,
            "seq": seq,
            "ver": ver,
            "payload": decoded_payload,
        }

    def _safe_decompress(
        self,
        data: bytes,
        start_uncompressed_size: int = 100,
        coefficient: int = 2,
        max_retries: int = 6,
    ) -> bytes | None:
        """Safe decompress.

        :param data: Data what need to be decompressed.
        :type data: bytes
        :param start_uncompressed_size: The start uncompressed size value.
        :type start_uncompressed_size: int
        :param coefficient: The coefficient value.
        :type coefficient: int
        :param max_retries: The max retries value.
        :type max_retries: int
        :returns: The resulting bytes | None value.
        :rtype: bytes | None
        """
        uncompressed_size = start_uncompressed_size
        for _ in range(max_retries):
            try:
                uncompressed_data = lz4.block.decompress(
                    data,
                    uncompressed_size=uncompressed_size,
                )
                return cast(bytes, uncompressed_data)
            except lz4.block.LZ4BlockError:
                uncompressed_size *= coefficient
        else:
            return None

    def _create_packet(
        self, seq: int, opcode: int, cmd: int, ver: int, payload: Any
    ) -> bytes:
        """Create packet.

        :param seq: The seq value.
        :type seq: int
        :param opcode: The opcode value.
        :type opcode: int
        :param cmd: The cmd value.
        :type cmd: int
        :param ver: The ver value.
        :type ver: int
        :param payload: Payload to encode, decode, or validate.
        :type payload: Any
        :returns: The resulting bytes value.
        :rtype: bytes
        """
        packed_payload = msgpack.packb(payload)
        seq_b = seq.to_bytes(1, "big")
        cmd_b = cmd.to_bytes(2, "big")
        opcode_b = opcode.to_bytes(2, "big")
        ver_b = ver.to_bytes(1, "big")
        if packed_payload is None:
            payload_bytes = b""
        payload_len = len(packed_payload)
        payload_len_b = payload_len.to_bytes(4, "big")
        return cast(
            bytes, ver_b + cmd_b + seq_b + opcode_b + payload_len_b + packed_payload
        )

    async def _encode(self, request: dict[str, Any]) -> None:
        """Send.

        :param request: Protocol request envelope to populate or send.
        :type request: dict[str, Any]
        # :raises SocketTransportSendError: If request must be a dict with keys: "seq", "opcode", and "cmd".
        # :raises SocketTransportSendError: If the requested action cannot be completed.
        """
        # if not isinstance(request, dict):
        #     raise SocketTransportSendError(
        #         'request must be a dict with keys: "seq", "opcode", and "cmd"'
        #     )
        seq = int(request.get("seq", 0))
        opcode = int(request.get("opcode", 1))
        cmd = int(request.get("cmd", 0))
        ver = int(request.get("ver", 11))
        del request["seq"]
        del request["opcode"]
        del request["cmd"]
        if "ver" in request:
            del request["ver"]
        if not ver:
            ver = 11
        packet = self._create_packet(
            seq, opcode, cmd, ver, payload=request.get("payload")
        )
