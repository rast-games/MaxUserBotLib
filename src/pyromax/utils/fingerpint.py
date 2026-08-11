import hashlib
import json
import struct
from importlib import resources
from typing import Any

from pydantic import BaseModel


class ApkBuildFingerprint(BaseModel):
    signature_scheme: str
    certificate_count: int
    certificate_meta_sha256: str
    certificate_sha256: list[str]
    dex_meta_sha256: str
    so_meta_sha256: dict[str, str]
    build_number: int


class FingerprintGenerator:
    def __init__(
        self,
    ) -> None:
        """Initialize the fingerprint generator.
        """
        self.path = resources.files("pyromax._data") / "apk_fingerprints.json"
        self.data = self.load_fingerprints()

    def load_fingerprints(self) -> Any:
        """Load fingerprints.

        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def generate_fingerprint(
        self,
        version: str,
        device_id: str,
        calls_seed: int,
        arch: str = "arm64-v8a",
    ) -> bytes | None:
        """Generate fingerprint.

        :param version: The version value.
        :type version: str
        :param device_id: Identifier of the device.
        :type device_id: str
        :param calls_seed: The calls seed value.
        :type calls_seed: int
        :param arch: The arch value.
        :type arch: str
        :returns: The resulting bytes | None value.
        :rtype: bytes | None
        """
        data = self.data.get(version)
        if not data:
            return None

        model = ApkBuildFingerprint.model_validate(data)

        seed_bytes = struct.pack(">q", calls_seed)
        device_bytes = device_id.encode("utf-8")

        h1 = hashlib.sha256(
            bytes.fromhex(model.certificate_meta_sha256) + seed_bytes + device_bytes
        ).digest()
        h2 = hashlib.sha256(
            bytes.fromhex(model.dex_meta_sha256) + seed_bytes + device_bytes
        ).digest()
        h3 = hashlib.sha256(
            bytes.fromhex(model.so_meta_sha256[arch]) + seed_bytes + device_bytes
        ).digest()

        return h1 + h2 + h3
