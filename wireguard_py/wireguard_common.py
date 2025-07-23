# pyre-unsafe
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This software may be used and distributed according to the terms of the
MIT License.
"""
from random import random, randint
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import List, Optional, Union

IPAddress = Union[IPv4Address, IPv6Address]
IPNetwork = Union[IPv4Network, IPv6Network]

RandomPort = lambda : randint(40000, 60000)

@dataclass
class Endpoint:
    ip: Optional[IPAddress] = None
    port: int = field(default_factory=RandomPort)

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"


@dataclass
class Peer:
    pubkey: str
    privkey: Optional[str] = None
    interface: Optional[Endpoint] = None
    allowed_ips: List[IPNetwork] = field(default_factory=list)
    last_handshake_time: Optional[int] = None
    rx_bytes: Optional[int] = None
    tx_bytes: Optional[int] = None
    # ipaddress: Optional[IPAddress] = None
    dns: Optional[List[IPAddress]] = None

    def __str__(self) -> str:
        return self.pubkey
    
    def to_dict(self, gateway_endpoint: Endpoint, gateway_public_key: bytes) -> dict:
        return {
            "Interface": {
                "PrivateKey": self.privkey,
                "Address": self.interface.ip,
                "DNS": self.dns,
            },
            "Peer": {
                "PublicKey": gateway_public_key.decode(),
                "AllowedIPs": self.allowed_ips,
                "Endpoint": f"{gateway_endpoint.ip}:{gateway_endpoint.port}",
                "PersistentKeepalive": 25,
            }
        }
    
    def to_config(self, wireguard_interface):
        TEMPLATE = "[Interface]\n" \
        "PrivateKey = {peer_private_key}\n" \
        "Address = {peer_address}/32\n" \
        "DNS = {dns}\n\n" \
        "[Peer]\n" \
        "PublicKey = {interface_public_key}\n" \
        "AllowedIPs = {allowed_ips}\n" \
        "Endpoint = {endpoint}:{port}\n" \
        "PersistentKeepalive = 25"

        return TEMPLATE.format(
            allowed_ips=", ".join([str(allowed_ip) for allowed_ip in self.allowed_ips]), 
            interface_public_key=wireguard_interface.keypair.public_key(), 
            peer_private_key=self.privkey, 
            endpoint="192.168.19.126", # YOUR IP ADDRESS
            port=wireguard_interface.endpoint.port,
            peer_address=self.interface.ip,
            dns=self.dns if self.dns else "1.1.1.1")

        
