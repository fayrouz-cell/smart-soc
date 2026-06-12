"""Tests for packet parser."""

import pytest
from scapy.all import IP, IPv6, TCP, UDP, ICMP, Raw

from core.packet_parser import parse_packet, PacketRecord


def test_parse_tcp_packet(sample_tcp_packet):
    """Test parsing TCP packet."""
    result = parse_packet(sample_tcp_packet)
    assert result is not None
    assert result.protocol == "TCP"
    assert result.src == "192.168.1.10"
    assert result.dst == "192.168.1.5"
    assert result.sport == 51514
    assert result.dport == 80
    assert "S" in result.flags


def test_parse_udp_packet(sample_udp_packet):
    """Test parsing UDP packet."""
    result = parse_packet(sample_udp_packet)
    assert result is not None
    assert result.protocol == "UDP"
    assert result.src == "192.168.1.10"
    assert result.dst == "192.168.1.5"
    assert result.sport == 51514
    assert result.dport == 53


def test_parse_icmp_packet(sample_icmp_packet):
    """Test parsing ICMP packet."""
    result = parse_packet(sample_icmp_packet)
    assert result is not None
    assert result.protocol == "ICMP"
    assert result.src == "192.168.1.10"
    assert result.dst == "192.168.1.5"


def test_parse_packet_with_payload():
    """Test parsing packet with payload."""
    payload = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
    packet = IP(src="192.168.1.10", dst="192.168.1.5") / TCP(
        sport=51514, dport=80, flags="PA"
    ) / Raw(load=payload)

    result = parse_packet(packet)
    assert result is not None
    assert result.payload_size == len(payload)
    assert len(result.raw_payload) > 0


def test_parse_ipv6_packet():
    """Test parsing IPv6 packet."""
    packet = IPv6(src="2001:db8::1", dst="2001:db8::2") / TCP(sport=51514, dport=80, flags="S")
    result = parse_packet(packet)
    assert result is not None
    assert result.src == "2001:db8::1"
    assert result.dst == "2001:db8::2"
    assert result.protocol == "TCP"


def test_parse_invalid_packet():
    """Test parsing invalid packet."""
    # Non-IP packet should return None
    from scapy.all import Ether
    packet = Ether() / b"invalid"
    result = parse_packet(packet)
    assert result is None


def test_packet_record_to_dict(sample_packet_record):
    """Test PacketRecord to_dict method."""
    result = sample_packet_record.to_dict()
    assert isinstance(result, dict)
    assert result["src"] == "192.168.1.10"
    assert result["protocol"] == "TCP"


