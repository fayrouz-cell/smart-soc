"""Tests for packet sniffer."""

import pytest
from pathlib import Path
from core.sniffer import PacketSniffer
from core.packet_parser import PacketRecord


def test_sniffer_replay_mode(sample_pcap_path):
    """Test sniffer in replay mode."""
    sniffer = PacketSniffer(
        mode="replay",
        pcap_path=sample_pcap_path,
    )

    packets = list(sniffer.start())
    assert len(packets) > 0
    assert all(isinstance(p, PacketRecord) for p in packets)


def test_sniffer_stats(sample_pcap_path):
    """Test sniffer statistics."""
    sniffer = PacketSniffer(
        mode="replay",
        pcap_path=sample_pcap_path,
    )

    list(sniffer.start())
    stats = sniffer.get_stats()
    assert stats["packet_count"] > 0
    assert stats["mode"] == "replay"


def test_sniffer_stop(sample_pcap_path):
    """Test stopping sniffer."""
    sniffer = PacketSniffer(
        mode="replay",
        pcap_path=sample_pcap_path,
    )

    sniffer.stop()
    assert not sniffer.running


