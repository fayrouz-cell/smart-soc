"""Packet parsing module for IDS."""

import time
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from scapy.all import IP, IPv6, TCP, UDP, ICMP, Raw
from scapy.packet import Packet


@dataclass
class PacketRecord:
    """Standardized packet record structure."""

    ts: float
    src: str
    dst: str
    protocol: str
    sport: Optional[int] = None
    dport: Optional[int] = None
    flags: Optional[str] = None
    payload_size: int = 0
    raw_payload: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def parse_packet(packet: Packet) -> Optional[PacketRecord]:
    """
    Parse a scapy packet into a standardized PacketRecord.

    Args:
        packet: Scapy packet object

    Returns:
        PacketRecord or None if packet cannot be parsed
    """
    try:
        # Extract timestamp
        if hasattr(packet, "time"):
            ts = float(packet.time)
        else:
            ts = time.time()

        # Extract IP layer
        ip_layer = None
        if packet.haslayer(IP):
            ip_layer = packet[IP]
            src = ip_layer.src
            dst = ip_layer.dst
        elif packet.haslayer(IPv6):
            ip_layer = packet[IPv6]
            src = ip_layer.src
            dst = ip_layer.dst
        else:
            return None

        # Determine protocol
        protocol = "UNKNOWN"
        sport = None
        dport = None
        flags = None
        payload_size = 0
        raw_payload = ""

        # Parse transport layer
        if packet.haslayer(TCP):
            tcp = packet[TCP]
            protocol = "TCP"
            sport = tcp.sport
            dport = tcp.dport
            flags = _parse_tcp_flags(tcp.flags) # Convertit les bits en texte (ex: "SA")
            if packet.haslayer(Raw):
                payload = bytes(packet[Raw].load)
                payload_size = len(payload)
                raw_payload = _safe_hex_convert(payload)

        elif packet.haslayer(UDP):
            udp = packet[UDP]
            protocol = "UDP"
            sport = udp.sport
            dport = udp.dport
            if packet.haslayer(Raw):
                payload = bytes(packet[Raw].load)
                payload_size = len(payload)
                raw_payload = _safe_hex_convert(payload)

        elif packet.haslayer(ICMP):
            icmp = packet[ICMP]
            protocol = "ICMP"
            # ICMP doesn't have ports, but we can use type/code
            if hasattr(icmp, "type"):
                sport = icmp.type
            if hasattr(icmp, "code"):
                dport = icmp.code

        # Calculate total payload size if not already set
        if payload_size == 0:
            if packet.haslayer(Raw):
                payload = bytes(packet[Raw].load)
                payload_size = len(payload)
                raw_payload = _safe_hex_convert(payload)
            else:
                # Estimate from packet length
                payload_size = max(0, len(packet) - (len(ip_layer) if ip_layer else 0))

        return PacketRecord(
            ts=ts,
            src=src,
            dst=dst,
            protocol=protocol,
            sport=sport,
            dport=dport,
            flags=flags,
            payload_size=payload_size,
            raw_payload=raw_payload,
        )

    except Exception as e:
        # Log parsing errors but don't crash
        return None


def _parse_tcp_flags(flags: int) -> str:
    """
    Parse TCP flags integer to string representation.

    Args:
        flags: TCP flags as integer

    Returns:
        String of flag letters (e.g., "SA" for SYN+ACK)
    """
    flag_chars = []
    if flags & 0x01:  # FIN
        flag_chars.append("F")
    if flags & 0x02:  # SYN
        flag_chars.append("S")
    if flags & 0x04:  # RST
        flag_chars.append("R")
    if flags & 0x08:  # PSH
        flag_chars.append("P")
    if flags & 0x10:  # ACK
        flag_chars.append("A")
    if flags & 0x20:  # URG
        flag_chars.append("U")
    return "".join(flag_chars) if flag_chars else ""


def _safe_hex_convert(data: bytes, max_length: int = 512) -> str:
    """
    Convert bytes to hex string safely.

    Args:
        data: Bytes to convert
        max_length: Maximum hex string length

    Returns:
        Hex string
    """
    if not data:
        return ""
    hex_str = data.hex()
    if len(hex_str) > max_length:
        return hex_str[:max_length] + "..."
    return hex_str
