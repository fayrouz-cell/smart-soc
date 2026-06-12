#!/usr/bin/env python3
"""Main entry point for IDS."""

import sys
import signal
import argparse
from pathlib import Path
from typing import Optional

from core.utils import load_config
from core.sniffer import PacketSniffer
from core.packet_parser import PacketRecord
from core.signature_engine import SignatureEngine
from core.anomaly_engine import AnomalyEngine
from core.logger import get_logger, log_packet_json, log_alert_json
from core.alert import Alert, AlertManager
from cli.interface import CLIInterface

__version__ = "1.0.0"


class IDS:
    """Main IDS application."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize IDS.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.running = False
        self.packet_count = 0
        self.alert_count = 0

        # Setup logging
        log_config = self.config.get("logging", {})
        self.traffic_logger = get_logger(
            "traffic",
            log_file=log_config.get("traffic_log"),
            max_bytes=log_config.get("max_bytes", 10485760),
            backup_count=log_config.get("backup_count", 7),
        )
        self.alerts_logger = get_logger(
            "alerts",
            log_file=log_config.get("alerts_log"),
            max_bytes=log_config.get("max_bytes", 10485760),
            backup_count=log_config.get("backup_count", 7),
        )

        # Setup alert manager
        self.alert_manager = AlertManager()

        # Setup detection engines
        self.signature_engine = SignatureEngine(self.config, self._handle_alert)
        self.anomaly_engine = AnomalyEngine(self.config, self._handle_alert)

        # Setup sniffer
        capture_config = self.config.get("capture", {})
        self.sniffer = PacketSniffer(
            mode=capture_config.get("mode", "replay"),
            interface=capture_config.get("interface"),
            pcap_path=capture_config.get("pcap_path"),
            bpf_filter=capture_config.get("bpf_filter", ""),
            throttle_packets_per_sec=capture_config.get("throttle_packets_per_sec", 0),
            packet_callback=self._handle_packet,
        )

        # Setup signal handlers (only works in main thread)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError:
            # Signal handlers can only be set in main thread
            # This is expected when running from Flask/web interface in a thread
            pass

    def _handle_packet(self, packet_record: PacketRecord) -> None:
        """
        Handle a parsed packet.

        Args:
            packet_record: Parsed packet record
        """
        self.packet_count += 1
        packet_dict = packet_record.to_dict()

        # Log packet
        log_packet_json(self.traffic_logger, packet_dict)

        # Process through detection engines
        self.signature_engine.process_packet(packet_dict)
        self.anomaly_engine.process_packet(packet_dict)

    def _handle_alert(self, alert: Alert) -> None:
        """
        Handle an alert.

        Args:
            alert: Alert object
        """
        self.alert_count += 1
        alert_dict = alert.to_dict()

        # Log alert
        log_alert_json(self.alerts_logger, alert_dict)

        # Display alert
        self.alert_manager.display_alert(alert)

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        print("\nShutting down IDS...")
        self.stop()

    def start(self) -> None:
        """Start IDS."""
        self.running = True
        print("Starting IDS...")
        print(f"Mode: {self.sniffer.mode}")
        print(f"Config loaded from: {self.config.get('_config_path', 'default')}")

        try:
            for packet in self.sniffer.start():
                if not self.running:
                    break
                # Packets are handled via callback
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error during capture: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop IDS."""
        self.running = False
        self.sniffer.stop()
        print(f"\nIDS stopped. Processed {self.packet_count} packets, generated {self.alert_count} alerts.")

    def get_stats(self) -> dict:
        """
        Get IDS statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "packet_count": self.packet_count,
            "alert_count": self.alert_count,
            "running": self.running,
            "sniffer_stats": self.sniffer.get_stats(),
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Network Intrusion Detection System")
    parser.add_argument("--start", action="store_true", help="Start IDS")
    parser.add_argument(
        "--mode",
        choices=["live", "replay"],
        default="replay",
        help="Capture mode (default: replay)",
    )
    parser.add_argument("--interface", help="Network interface for live capture")
    parser.add_argument("--pcap", help="PCAP file path for replay mode")
    parser.add_argument("--stats", action="store_true", help="Show statistics and exit")
    parser.add_argument("--show-alerts", action="store_true", help="Show recent alerts")
    parser.add_argument("--tail", type=int, help="Show last N alerts")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Validate config and exit")
    parser.add_argument("--version", action="version", version=f"IDS {__version__}")

    args = parser.parse_args()

    # Load config
    try:
        ids = IDS(config_path=args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Dry run
    if args.dry_run:
        print("Configuration validated successfully.")
        sys.exit(0)

    # Show stats
    if args.stats:
        stats = ids.get_stats()
        cli = CLIInterface()
        cli.display_stats(stats)
        sys.exit(0)

    # Show alerts
    if args.show_alerts:
        cli = CLIInterface()
        log_config = ids.config.get("logging", {})
        alerts_log = log_config.get("alerts_log", "data/logs/alerts.log")
        alerts = cli.read_alerts_from_log(alerts_log, tail=args.tail)
        cli.display_alerts(alerts, tail=args.tail)
        sys.exit(0)

    # Override config with CLI args
    if args.mode:
        ids.sniffer.mode = args.mode
    if args.interface:
        ids.sniffer.interface = args.interface
    if args.pcap:
        ids.sniffer.pcap_path = args.pcap

    # Start IDS
    if args.start:
        ids.start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


