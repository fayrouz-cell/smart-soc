"""Tests for anomaly engine."""

import pytest
import time
from core.anomaly_engine import AnomalyEngine
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
def anomaly_engine(test_config, alert_callback):
    """Create anomaly engine for testing."""
    return AnomalyEngine(test_config, alert_callback)


def test_high_packet_rate_anomaly(anomaly_engine, alert_callback):
    """Test high packet rate anomaly detection."""
    src_ip = "192.168.1.10"
    base_time = time.time()

    # Generate many packets quickly (simulating high rate)
    for i in range(2000):  # More than threshold of 1000 per minute
        packet = {
            "src": src_ip,
            "dst": "192.168.1.5",
            "protocol": "TCP",
            "payload_size": 100,
            "ts": base_time + i * 0.01,  # Fast rate
        }
        anomaly_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "ANOMALY_HIGH_RATE" for alert in alert_callback.alerts)


def test_large_payload_anomaly(anomaly_engine, alert_callback):
    """Test large payload anomaly detection."""
    src_ip = "192.168.1.10"
    base_time = time.time()

    # Generate packets with large payloads
    for i in range(20):
        packet = {
            "src": src_ip,
            "dst": "192.168.1.5",
            "protocol": "TCP",
            "payload_size": 15000,  # Larger than threshold of 10000
            "ts": base_time + i * 0.1,
        }
        anomaly_engine.process_packet(packet)

    # Should have triggered an alert
    assert len(alert_callback.alerts) > 0
    assert any(alert.rule == "ANOMALY_LARGE_PAYLOAD" for alert in alert_callback.alerts)


