"""Network packet sniffer module."""

import time
import sys
from pathlib import Path
from typing import Iterator, Optional, Callable
from scapy.all import sniff, rdpcap, get_if_list
from scapy.packet import Packet

from core.packet_parser import parse_packet, PacketRecord


class PacketSniffer:
    """Network packet sniffer with live and replay modes."""

    def __init__(
        self,
        mode: str = "replay",
        interface: Optional[str] = None,
        pcap_path: Optional[str] = None,
        bpf_filter: str = "",
        throttle_packets_per_sec: int = 0,
        packet_callback: Optional[Callable[[PacketRecord], None]] = None,
    ):
        """
        Initialize packet sniffer.

        Args:
            mode: Capture mode ('live' or 'replay')
            interface: Network interface for live capture
            pcap_path: Path to PCAP file for replay
            bpf_filter: BPF filter string
            throttle_packets_per_sec: Throttle rate (0 = no throttle)
            packet_callback: Callback function for each parsed packet
        """
        self.mode = mode
        self.interface = interface
        self.pcap_path = pcap_path
        self.bpf_filter = bpf_filter
        self.throttle_packets_per_sec = throttle_packets_per_sec
        self.packet_callback = packet_callback
        self.running = False
        self.packet_count = 0

    def start(self) -> Iterator[PacketRecord]:
        """
        Start packet capture and yield parsed packets.

        Yields:
            PacketRecord objects
        """
        self.running = True
        self.packet_count = 0

        if self.mode == "live":
            yield from self._capture_live()
        elif self.mode == "replay":
            yield from self._capture_replay()
        else:
            raise ValueError(f"Unknown capture mode: {self.mode}")

    def _capture_live(self) -> Iterator[PacketRecord]:
        """Capture packets from live interface."""
        if not self.interface:
            # Try to auto-detect interface (prefer WiFi)
            interfaces = get_if_list()
            if not interfaces:
                raise ValueError("No network interface available")
            
            # Try to find WiFi interface first (better detection)
            wifi_interface = None
            for iface in interfaces:
                iface_lower = iface.lower()
                # More comprehensive WiFi detection
                wifi_keywords = ["wi", "wlan", "wireless", "wifi", "802.11"]
                if any(keyword in iface_lower for keyword in wifi_keywords):
                    # Check if it has an IP address (likely connected)
                    try:
                        from scapy.all import get_if_addr
                        addr = get_if_addr(iface)
                        if addr and addr != "0.0.0.0":
                            wifi_interface = iface
                            break
                    except Exception:
                        pass
                    # If no IP check, still prefer WiFi
                    if not wifi_interface:
                        wifi_interface = iface
            
            self.interface = wifi_interface if wifi_interface else interfaces[0]
            if wifi_interface:
                print(f"✓ Auto-detected WiFi interface: {self.interface}")
            else:
                print(f"⚠ No WiFi interface found, using: {self.interface}")

        print(f"Starting live capture on interface: {self.interface}")
        print("Note: This requires root/admin privileges on most systems")

        try:
            last_packet_time = time.time()
            min_interval = 1.0 / self.throttle_packets_per_sec if self.throttle_packets_per_sec > 0 else 0

            def packet_handler(packet: Packet) -> None:
                """Handle each captured packet."""
                if not self.running:
                    return

                # Throttle if configured
                if self.throttle_packets_per_sec > 0:
                    current_time = time.time()
                    elapsed = current_time - last_packet_time
                    if elapsed < min_interval:
                        time.sleep(min_interval - elapsed)

                parsed = parse_packet(packet)
                if parsed:
                    self.packet_count += 1
                    if self.packet_callback:
                        self.packet_callback(parsed)
                    # Note: yield doesn't work in callback, so we use callback instead

            # Start sniffing
            sniff(
                iface=self.interface,
                filter=self.bpf_filter,
                prn=packet_handler,
                promisc=True,
                stop_filter=lambda x: not self.running,
            )

        except PermissionError:
            print("ERROR: Permission denied. Live capture requires root/admin privileges.")
            print("Please run with sudo/administrator rights, or use --mode replay")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to start live capture: {e}")
            print("Falling back to replay mode...")
            self.mode = "replay"
            yield from self._capture_replay()

    def _capture_replay(self) -> Iterator[PacketRecord]:
        """Replay packets from PCAP file."""
        if not self.pcap_path:
            raise ValueError("PCAP path required for replay mode")

        pcap_file = Path(self.pcap_path)
        if not pcap_file.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_file}")

        print(f"Replaying packets from: {pcap_file}")

        try:
            packets = rdpcap(str(pcap_file))
            last_packet_time = None
            min_interval = 1.0 / self.throttle_packets_per_sec if self.throttle_packets_per_sec > 0 else 0

            for packet in packets:
                if not self.running:
                    break

                # Throttle if configured
                if self.throttle_packets_per_sec > 0 and last_packet_time is not None:
                    current_time = time.time()
                    elapsed = current_time - last_packet_time
                    if elapsed < min_interval:
                        time.sleep(min_interval - elapsed)

                parsed = parse_packet(packet)
                if parsed:
                    self.packet_count += 1
                    if self.packet_callback:
                        self.packet_callback(parsed)
                    yield parsed
                    last_packet_time = time.time()

            print(f"Replayed {self.packet_count} packets")

        except Exception as e:
            print(f"ERROR: Failed to replay PCAP: {e}")
            raise

    def stop(self) -> None:
        """Stop packet capture."""
        self.running = False

    def get_stats(self) -> dict:
        """
        Get capture statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "mode": self.mode,
            "packet_count": self.packet_count,
            "running": self.running,
        }


