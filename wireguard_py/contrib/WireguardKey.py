
from __future__ import annotations

from base64 import standard_b64encode, urlsafe_b64decode, urlsafe_b64encode
from secrets import token_bytes

from attrs import define, field

import wireguard_py as wg

def convert_wireguard_key(value: str | bytes | WireguardKey) -> bytes:
    """Decode a wireguard key to its byte string form.
    """
    if isinstance(value, WireguardKey):
        return value.keydata

    if isinstance(value, bytes):
        raw_key = value
    elif isinstance(value, str):
        # raw_key = bytes.fromhex(value)
        raw_key = value.encode('utf-8')
    else:
        pass

    return raw_key


@define(frozen=True)
class WireguardKey:
    """Representation of a WireGuard key."""

    keydata: bytes = field(converter=convert_wireguard_key)

    @classmethod
    def generate(cls) -> WireguardKey:
        """Generate a new private key."""
        private_bytes = wg.gen_priv_key()
        return cls(private_bytes)

    def public_key(self) -> WireguardKey:
        """Derive public key from private key."""
        public_bytes = wg.get_pub_key(self.keydata)
        return WireguardKey(public_bytes)

    def private_key(self) -> WireguardKey:
        """Derive private key from private key."""
        return self

    def __bool__(self) -> bool:
        return int.from_bytes(self.keydata, "little") != 0
    
    def __int__(self, ) -> bool:
        return int.from_bytes(self.keydata, "little")

    def __repr__(self) -> str:
        return f"WireguardKey({self.keydata})"

    def __str__(self) -> str:
        """Return a base64 encoded representation of the key."""
        return self.keydata.decode("utf-8")

    @property
    def urlsafe(self) -> str:
        """Return a urlsafe base64 encoded representation of the key."""
        return urlsafe_b64encode(self.keydata).decode("utf-8").rstrip("=")

    @property
    def hex(self) -> str:
        """Return a hexadecimal encoded representation of the key."""
        return self.keydata.hex()