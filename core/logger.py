"""Logging module for IDS."""

import json
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional
from datetime import datetime

from core.utils import ensure_directory, restrict_file_permissions, get_iso_timestamp


def get_logger(name: str, log_file: Optional[str] = None, max_bytes: int = 10485760, backup_count: int = 7) -> logging.Logger:
    """
    Get or create a logger with rotating file handler.

    Args:
        name: Logger name
        log_file: Optional log file path
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if path provided
    if log_file:
        log_path = Path(log_file)
        ensure_directory(log_path.parent)
        file_handler = RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Restrict permissions if on Unix-like system
        try:
            restrict_file_permissions(log_path)
        except Exception:
            pass

    return logger


def log_packet_json(logger: logging.Logger, packet_record: Dict[str, Any]) -> None:
    """
    Log a packet record as JSON line.

    Args:
        logger: Logger instance
        packet_record: Packet record dictionary
    """
    # Add ISO timestamp
    log_entry = {
        "timestamp": get_iso_timestamp(),
        "packet": packet_record,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))


def log_alert_json(logger: logging.Logger, alert: Dict[str, Any]) -> None:
    """
    Log an alert as JSON line.

    Args:
        logger: Logger instance
        alert: Alert dictionary
    """
    # Ensure timestamp is ISO format
    if "ts" in alert:
        alert["timestamp"] = get_iso_timestamp()
    logger.info(json.dumps(alert, ensure_ascii=False))


