"""Tests for signature engine."""

import pytest
import time
from core.signature_engine import SignatureEngine
from core.alert import Alert


@pytest.fixture
def alert_callback():
    """Create alert callback for testing."""
    alerts = []

    def callback(alert: Alert):
        alerts.append(alert)

    callback.alerts = alerts
    return callback


@pytest.fixture
def signature_engine(test_config, alert_callback):
    """Create signature engine for testing."""
    return SignatureEngine(test_config, alert_callback)


def test_port_scan_detection(signature_engine, alert_callback):
    """Test port scan detection."""
    src_ip = "192.168.1.14"
    base_time = time.time()

    # Generate packets to trigger port scan (25 ports > threshold of 20)
    for port in range(1, 26):
        packet = {
            "src": src_ip,
            "dst": "192.168.1.5",
            "protocol": "TCP",
            "dport": port,
            "ts": base_time + port * 0.1,
        }
        signature_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "PORT_SCAN" for alert in alert_callback.alerts)


def test_syn_flood_detection(signature_engine, alert_callback):
    """Test SYN flood detection."""
    src_ip = "192.168.1.15"
    base_time = time.time()

    # Generate 200+ SYN packets (threshold is 200)
    for i in range(201):
        packet = {
            "src": src_ip,
            "dst": "192.168.1.5",
            "protocol": "TCP",
            "dport": 80,
            "flags": "S",
            "ts": base_time + i * 0.01,
        }
        signature_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "SYN_FLOOD" for alert in alert_callback.alerts)


def test_ping_sweep_detection(signature_engine, alert_callback):
    """Test ping sweep detection."""
    src_ip = "192.168.1.16"
    base_time = time.time()

    # Generate 50+ ICMP echo requests (threshold is 50)
    for i in range(51):
        packet = {
            "src": src_ip,
            "dst": f"192.168.1.{i+1}",
            "protocol": "ICMP",
            "sport": 8,  # ICMP echo request
            "ts": base_time + i * 0.1,
        }
        signature_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "PING_SWEEP" for alert in alert_callback.alerts)


def test_suspicious_port_detection(signature_engine, alert_callback):
    """Test suspicious port detection."""
    packet = {
        "src": "192.168.1.10",
        "dst": "192.168.1.5",
        "protocol": "TCP",
        "dport": 22,  # SSH - suspicious port
        "ts": time.time(),
    }
    signature_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "SUSPICIOUS_PORT" for alert in alert_callback.alerts)


