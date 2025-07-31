from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Dict, List, Optional

import pyroute2
import wireguard_py
from wireguard_py.peers import Endpoint, Peer
from wireguard_py.keys import WireguardKey


class WireGuardInterface:
    name : str
    cidr : IPv4Network | IPv6Network
    endpoint: Endpoint
    peers : Dict[str, Peer]
    keypair : WireguardKey
    ip : Optional[IPv4Address | IPv6Address]

    _ipr_ : pyroute2.IPRoute
    _status_ : bool

    def __init__(self, 
                 interface_name: str, 
                 cidr: IPv4Network | IPv6Network,
                 peers: Optional[Dict[str, Peer]] = None,
                 keypair: Optional[WireguardKey] = None,
                 endpoint: Optional[Endpoint] = None,
                 ip : Optional[IPv4Address | IPv6Address] = None,
                 ipr : Optional[pyroute2.IPRoute] = None
        ):
        self.name : str = interface_name
        self.cidr : IPv4Network | IPv6Network = cidr
        self.peers : Dict[str, Peer] = peers if peers else {}
        self.keypair : WireguardKey = keypair if keypair else WireguardKey.generate()
        self.endpoint : Optional[Endpoint] = endpoint if endpoint else Endpoint()
        self.ip : Optional[IPv4Address | IPv6Address] = ip

        self._ipr_ = ipr if ipr else pyroute2.IPRoute()
        self._status_ : bool = False

    @property
    def status(self, ) -> bool:
        return bool(self._ipr_.link_lookup(ifname=self.name))

    def get_used_ips(self, ) -> List[IPv4Address | IPv6Address]:
        __list__ = []
        for peer_name, peer in self.peers.items():
            if peer.interface.ip:
                __list__.append(peer.interface.ip)
        return __list__

    def get_next_available_ip(self, ) -> IPv4Address | IPv6Address:
        __used_ips__ = self.get_used_ips()
        for host in self.cidr.hosts():
            if host not in __used_ips__:
                return host

    def assign_ip(self, ip: IPv4Address | IPv6Network):
        __old_state__ = False # Variable to save the current state of the interface ( Up or Down )
    
        if __old_state__ := self.status:
            self.bring_down() # If Up, take it down first
    
        self.ip = ip
    
        if __old_state__:
            # It the interface was Up, make it Up again
            self.bring_up()

    def add_peer(self, peer: Peer):
        self.peers[peer.name] = peer

    def bring_up(self):
        # Creates wg interface, sets keys, IP, brings interface up
        # Adds all peers
        self._ipr_.link("add", ifname=self.name, kind="wireguard")
        wg_ifc = self._ipr_.link_lookup(ifname=self.name)[0]

        # If ip for the interface is not defined, choose from within
        if not self.ip:
            self.ip = self.get_next_available_ip()

        # Add interface
        self._ipr_.addr("add", index=wg_ifc, address=str(self.ip), prefixlen=self.cidr.prefixlen)
        # Up interface
        self._ipr_.link("set", index=wg_ifc, state="up")

        # Configure it as a wireguard interface
        wireguard_py.set_device(
            device_name=self.name.encode(),
            priv_key=self.keypair.private_key().keydata, # Interface Private Key
            port=self.endpoint.port,
        )

        for peer_name, peer in self.peers.items():
            # Create a peer
            wireguard_py.set_peer(
                device_name=self.name.encode(),
                pub_key=peer.pubkey.encode(),     # Peer Public Key
                endpoint=peer.interface,
                allowed_ips=set(peer.allowed_ips),
                replace_allowed_ips=True,
            )

    def bring_down(self):
        # Creates wg interface, sets keys, IP, brings interface up
        # Adds all peers
        if wg_ifc := self._ipr_.link_lookup(ifname=self.name):
            self._ipr_.link("del", index=wg_ifc[0])
            if not self._ipr_.link_lookup(ifname=self.name):
                return True
        return False