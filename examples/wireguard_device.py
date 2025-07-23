import wireguard_py as wg
import ipaddress
import pyroute2
import wireguard_py
from wireguard_py.wireguard_common import Endpoint
from wireguard_py.contrib.WireguardDevice import WireguardDevice

def main():
    # Create the wireguard interface
    ipr = pyroute2.IPRoute()
    ipr.link("add", ifname="wg0", kind="wireguard")
    wg_ifc = ipr.link_lookup(ifname="wg0")[0]
    ipr.addr("add", index=wg_ifc, address="172.16.0.1", prefixlen=24)
    ipr.link("set", index=wg_ifc, state="up")

    # Configure wireguard interface
    priv_key = wireguard_py.gen_priv_key()
    wireguard_py.set_device(
        device_name=b"wg0",
        priv_key=priv_key,
        port=51820,
    )

    # Create a peer
    wireguard_py.set_peer(
        device_name=b"wg0",
        pub_key=b"lM77O8LlU4PNI0ZPWsTPYS3SGubG2/YT26uh9o9LKzM=",
        endpoint=Endpoint(ip=ipaddress.ip_address("172.16.0.2"), port=51820),
        allowed_ips={
            ipaddress.ip_network("172.16.0.2/32"),
            ipaddress.ip_network("10.0.0.0/8"),
        },
        replace_allowed_ips=True,
    )

    # List peers
    peers = wireguard_py.list_peers(b"wg0")
    print(peers)
    ifnames = [device.interface for device in WireguardDevice.list()]
    device = WireguardDevice.get("wg0")
    wgconfig = device.get_config()
    device.set_config(wgconfig)

    # Remove Wireguard iface
    wg_ifc = ipr.link_lookup(ifname="wg0")
    if wg_ifc:
        ipr.link("del", index=wg_ifc[0])

if __name__ == "__main__":
    main()

