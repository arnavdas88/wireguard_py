import wireguard_py as wg
from wireguard_py.contrib.WireguardKey import WireguardKey

def main():
    priv_key = WireguardKey(b"IICoxfMPrzOJnD7XfFIslcrxR/ztm1Sr8vo1V/os/kQ=")
    pub_key = WireguardKey(b"34cqsYrb2IeWYz2Gi2ElcBzC55k5sBLClNG8twOkEho=")

    assert priv_key.public_key() == pub_key
    pass

if __name__ == "__main__":
    main()