import ipaddress
import pyroute2
import wireguard_py
from wireguard_py.peers import Endpoint

#.               My Private Key                                   My Public Key
INTERFACE_KEY = (b'yO+XDIp4FP7jqjTJkYQuN6VI+r9heqoUjVSVvoGwf3w=', b'q3tCMnHy+jtQiEGNDRrD+ggYihUpRMRo3Er9Lu+OaHI=')
#            Peer Private Key                                 Peer Public Key
PEER_KEY = (b'kCZHwpflKBj6tSyHkeoqlnC/31NRtgBpRUjw1u/w81Q=', b'jEm7w1hXGaUe+wGv3Fc2ES5VRmAjL6+yZ16bImWO8T4=')

TEMPLATE = """
[Interface]
PrivateKey = {peer_private_key}
Address = 172.16.0.2/32
DNS = 172.31.31.31, 1.1.1.1

[Peer]
PublicKey = {interface_public_key}
AllowedIPs = {allowed_ips}
Endpoint = {endpoint}:{port}
PersistentKeepalive = 25
"""
PORT = 51820

def main():
    # Create the wireguard interface
    ipr = pyroute2.IPRoute()
    wg_ifc = ipr.link_lookup(ifname="wg0")
    if wg_ifc:
        ipr.link("del", index=wg_ifc[0])
    ipr.link("add", ifname="wg0", kind="wireguard")
    wg_ifc = ipr.link_lookup(ifname="wg0")[0]
    ipr.addr("add", index=wg_ifc, address="172.16.0.1", prefixlen=24)
    ipr.link("set", index=wg_ifc, state="up")

    # Configure wireguard interface
    wireguard_py.set_device(
        device_name=b"wg0",
        priv_key=INTERFACE_KEY[0], # Interface Private Key
        port=PORT,
    )

    # Create a peer
    wireguard_py.set_peer(
        device_name=b"wg0",
        pub_key=PEER_KEY[1],     # Peer Public Key
        endpoint=Endpoint(ip=ipaddress.ip_address("172.16.0.2"), port=51820),
        allowed_ips={
            ipaddress.ip_network("172.16.0.2/32"),
            # ipaddress.ip_network("10.0.0.0/8"),
        },
        replace_allowed_ips=True,
    )

    # List peers
    peers = wireguard_py.list_peers(b"wg0")
    print(peers)
    print(TEMPLATE.format(
        allowed_ips="172.16.0.1/24", 
        interface_public_key=INTERFACE_KEY[1].decode(), 
        peer_private_key=PEER_KEY[0].decode(), 
        endpoint="192.168.19.126", # YOUR IP ADDRESS
        port=PORT)
    )

    while True:
        py_cmd = input(">>> ")
        try:
            result = eval(py_cmd)
        except Exception as ex:
            result = ex
        print(result)

if __name__ == "__main__":
    main()