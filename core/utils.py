"""Utility functions for IDS project."""

import os
import stat
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load YAML configuration file with defaults.

    Args:
        config_path: Path to config file, defaults to config.yaml in project root

    Returns:
        Dictionary with configuration
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Set defaults if missing
    defaults = {
        "capture": {
            "mode": "replay",
            "interface": "eth0",
            "pcap_path": "data/pcap_samples/sample_traffic.pcap",
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
            "model_path": "data/datasets/isof_model.joblib",
            "baseline_path": "data/datasets/baseline_train.csv",
        },
        "logging": {
            "traffic_log": "data/logs/traffic.log",
            "alerts_log": "data/logs/alerts.log",
            "max_bytes": 10485760,
            "backup_count": 7,
            "level": "INFO",
        },
        "security": {"restrict_log_permissions": True},
    }

    # Merge with defaults
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                if subkey not in config[key]:
                    config[key][subkey] = subvalue

    return config


def safe_hex_convert(data: bytes, max_length: int = 512) -> str:
    """
    Convert bytes to hex string, truncating if too long.

    Args:
        data: Bytes to convert
        max_length: Maximum length of hex string

    Returns:
        Hex string representation
    """
    if not data:
        return ""
    hex_str = data.hex()
    if len(hex_str) > max_length:
        return hex_str[:max_length] + "..."
    return hex_str


def normalize_ip(ip: str) -> str:
    """
    Normalize IP address string.

    Args:
        ip: IP address string

    Returns:
        Normalized IP address
    """
    return ip.strip()


def ensure_directory(path: Path) -> None:
    """
    Ensure directory exists, create if not.

    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def restrict_file_permissions(file_path: Path) -> None:
    """
    Restrict file permissions to owner only (Unix-like systems).

    Args:
        file_path: Path to file
    """
    try:
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, AttributeError):
        # Windows or permission error, skip
        pass


def parse_time_window(seconds: float) -> float:
    """
    Parse time window in seconds.

    Args:
        seconds: Time in seconds

    Returns:
        Time in seconds as float
    """
    return float(seconds)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO8601 format.

    Returns:
        ISO8601 timestamp string
    """
    return datetime.utcnow().isoformat() + "Z"


