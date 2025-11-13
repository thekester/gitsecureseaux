#!/usr/bin/env python3
"""Extract the negotiated TLS cipher suite from a PCAP/PCAPNG file."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Tuple

from scapy.all import rdpcap  # type: ignore
from scapy.layers.tls.record import TLS  # type: ignore


SERVER_HELLO = 2  # TLS handshake message type
DEFAULT_PCAP = Path(__file__).with_name("challenge.pcapng")


def find_cipher_suite(pcap_path: str) -> Tuple[Optional[int], Optional[str]]:
    """Return the cipher suite code and its human-readable name."""
    packets = rdpcap(pcap_path)
    for packet in packets:
        if not packet.haslayer(TLS):
            continue
        tls_layer = packet[TLS]
        for handshake in getattr(tls_layer, "msg", []):
            if getattr(handshake, "msgtype", None) != SERVER_HELLO:
                continue
            cipher_code = getattr(handshake, "cipher", None)
            if cipher_code is None:
                continue
            field = handshake.get_field("cipher")
            cipher_name = field.i2s.get(cipher_code, f"unknown (0x{cipher_code:04x})")
            return cipher_code, cipher_name
    return None, None


def main() -> None:
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} [pcap/pcapng file]", file=sys.stderr)
        sys.exit(1)

    pcap_path = sys.argv[1] if len(sys.argv) == 2 else str(DEFAULT_PCAP)
    if not Path(pcap_path).is_file():
        print(f"Capture file not found: {pcap_path}", file=sys.stderr)
        sys.exit(1)

    cipher_code, cipher_name = find_cipher_suite(pcap_path)
    if cipher_code is None:
        print("No TLS ServerHello handshake found.")
        sys.exit(2)
    print(f"Negotiated cipher suite: {cipher_name} (0x{cipher_code:04x})")


if __name__ == "__main__":
    main()
