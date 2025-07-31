from wireguard_py.keys import WireguardKey
from wireguard_py.interface import WireGuardInterface
from wireguard_py.peers import Endpoint, Peer
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network


def main():
    peer_key = WireguardKey("kCZHwpflKBj6tSyHkeoqlnC/31NRtgBpRUjw1u/w81Q=") # Peer Private Key
    interface_key = WireguardKey("yO+XDIp4FP7jqjTJkYQuN6VI+r9heqoUjVSVvoGwf3w=") # Interface Private Key

    wg0 = WireGuardInterface(
        "wg-1101", 
        endpoint=Endpoint(ip = IPv4Address("172.10.10.1"), port=40262),
        cidr=IPv4Network("172.10.10.0/24"),
        keypair=interface_key,
        peers={
            "p1": Peer(
                pubkey=str(peer_key.public_key()), 
                privkey=str(peer_key.private_key()), # Not Compulsory
                interface=Endpoint(ip = IPv4Address("172.10.10.2")),
                allowed_ips=[ IPv4Network("172.10.10.0/24") ]
            )
        }
    )

    if wg0.status:
        wg0.bring_down()

    print(wg0.peers['p1'].to_config(wg0))

    wg0.bring_up()
    input("\nTunnel is Up ...")

    
    wg0.bring_down()
    input("\nTunnel is Down ...")


if __name__ == "__main__":
    main()