"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from scapy.all import IP, TCP, UDP, ICMP, RandShort
import time

from core.packet_parser import PacketRecord, parse_packet


@pytest.fixture
def sample_pcap_path(tmp_path):
    """Create a temporary sample PCAP file."""
    from scapy.all import wrpcap

    packets = []
    base_time = time.time()

    # Create some test packets
    for i in range(10):
        packet = IP(src=f"192.168.1.{i+1}", dst="192.168.1.100") / TCP(
            sport=RandShort(), dport=80, flags="S"
        )
        packet.time = base_time + i * 0.1
        packets.append(packet)

    pcap_file = tmp_path / "test.pcap"
    wrpcap(str(pcap_file), packets)
    return str(pcap_file)


@pytest.fixture
def sample_packet_record():
    """Create a sample packet record."""
    return PacketRecord(
        ts=time.time(),
        src="192.168.1.10",
        dst="192.168.1.5",
        protocol="TCP",
        sport=51514,
        dport=80,
        flags="S",
        payload_size=0,
        raw_payload="",
    )


@pytest.fixture
def sample_tcp_packet():
    """Create a sample TCP packet."""
    return IP(src="192.168.1.10", dst="192.168.1.5") / TCP(sport=51514, dport=80, flags="S")


@pytest.fixture
def sample_udp_packet():
    """Create a sample UDP packet."""
    return IP(src="192.168.1.10", dst="192.168.1.5") / UDP(sport=51514, dport=53)


@pytest.fixture
def sample_icmp_packet():
    """Create a sample ICMP packet."""
    return IP(src="192.168.1.10", dst="192.168.1.5") / ICMP(type=8)


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration."""
    import yaml
    from pathlib import Path

    config = {
        "capture": {
            "mode": "replay",
            "interface": "eth0",
            "pcap_path": str(tmp_path / "test.pcap"),
            "bpf_filter": "",
            "throttle_packets_per_sec": 0,
        },
        "signatures": {
            "portscan": {"enabled": True, "ports_threshold": 20, "window_seconds": 10},
            "syn_flood": {"enabled": True, "syn_threshold": 200, "window_seconds": 10},
            "ping_sweep": {"enabled": True, "hosts_threshold": 50, "window_seconds": 30},
            "suspicious_ports": {"enabled": True, "ports": [21, 22, 23, 3389, 4444, 6667]},
        },
        "anomaly": {
            "packet_rate_threshold": 1000,
            "payload_size_threshold_bytes": 10000,
            "use_ml": False,
            "model_path": str(tmp_path / "model.joblib"),
            "baseline_path": str(tmp_path / "baseline.csv"),
        },
        "logging": {
            "traffic_log": str(tmp_path / "traffic.log"),
            "alerts_log": str(tmp_path / "alerts.log"),
            "max_bytes": 10485760,
            "backup_count": 7,
            "level": "INFO",
        },
        "security": {"restrict_log_permissions": False},
    }

    return config


