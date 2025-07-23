from wireguard_py.WireguardInterface import WireGuardInterface
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

import wireguard_py
from wireguard_py.contrib.WireguardKey import WireguardKey
from wireguard_py.wireguard_common import Endpoint, Peer

p1key = WireguardKey("kCZHwpflKBj6tSyHkeoqlnC/31NRtgBpRUjw1u/w81Q=") # Peer Private Key
p1 = Peer(
    pubkey=str(p1key.public_key()), 
    privkey=str(p1key.private_key()),
    interface=Endpoint(ip = IPv4Address("172.10.10.2")),
    allowed_ips=[ IPv4Network("172.10.10.0/24") ]
)

wg0 = WireGuardInterface(
    "wg0", 
    cidr=IPv4Network("172.10.10.0/24"),
    keypair=WireguardKey("yO+XDIp4FP7jqjTJkYQuN6VI+r9heqoUjVSVvoGwf3w="), # Interface Private Key
    peers={
        "p1": p1
    }
)

if wg0.status:
    wg0.bring_down()

wg0.bring_up()
print(p1.to_config(wg0))

while True:
    e = input(">>>")
    print(f"{e}")
    if e == "exit\n":
        continue

wg0.bring_down()