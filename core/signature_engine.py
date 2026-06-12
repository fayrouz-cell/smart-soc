"""Signature-based detection engine."""

import time
import uuid
from collections import defaultdict, deque
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from core.alert import Alert


@dataclass
class WindowEntry:
    """Entry in sliding window."""

    timestamp: float
    data: Any


class SignatureEngine:
    """Signature-based intrusion detection engine."""

    def __init__(self, config: Dict[str, Any], alert_callback: Callable[[Alert], None]):
        """
        Initialize signature engine.

        Args:
            config: Configuration dictionary
            alert_callback: Callback function for alerts
        """
        self.config = config
        self.alert_callback = alert_callback
        self.signatures = config.get("signatures", {})

        # Port scan detection: track unique ports per source
        self.portscan_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.portscan_ports: Dict[str, set] = defaultdict(set)

        # SYN flood detection: track SYN packets per source
        self.syn_flood_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.syn_ack_counts: Dict[str, int] = defaultdict(int)

        # Ping sweep detection: track ICMP echo requests per source
        self.ping_sweep_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.ping_sweep_targets: Dict[str, set] = defaultdict(set)

        # Suspicious port access tracking
        self.suspicious_ports = set(self.signatures.get("suspicious_ports", {}).get("ports", []))

    def process_packet(self, packet_record: Dict[str, Any]) -> None:
        """
        Process a packet record and check against signature rules.

        Args:
            packet_record: Parsed packet record
        """
        src = packet_record.get("src")
        dst = packet_record.get("dst")
        protocol = packet_record.get("protocol")
        sport = packet_record.get("sport")
        dport = packet_record.get("dport")
        flags = packet_record.get("flags", "")
        ts = packet_record.get("ts", time.time())

        if not src or not dst:
            return

        # Check port scan
        if self.signatures.get("portscan", {}).get("enabled", False):
            self._check_portscan(src, dport, ts)

        # Check SYN flood
        if self.signatures.get("syn_flood", {}).get("enabled", False):
            if protocol == "TCP" and "S" in flags:
                self._check_syn_flood(src, flags, ts)

        # Check ping sweep
        if self.signatures.get("ping_sweep", {}).get("enabled", False):
            if protocol == "ICMP" and sport == 8:  # ICMP echo request
                self._check_ping_sweep(src, dst, ts)

        # Check suspicious ports
        if self.signatures.get("suspicious_ports", {}).get("enabled", False):
            if dport and dport in self.suspicious_ports:
                self._check_suspicious_port(src, dst, dport, ts)

    def _check_portscan(self, src: str, dport: Optional[int], ts: float) -> None:
        """Check for port scan pattern with enhanced detection."""
        if not dport:
            return

        config = self.signatures.get("portscan", {})
        threshold = config.get("ports_threshold", 20)
        window_seconds = config.get("window_seconds", 10)

        # Add to window
        self.portscan_windows[src].append(WindowEntry(ts, dport))
        self.portscan_ports[src].add(dport)

        # Clean old entries
        cutoff_time = ts - window_seconds
        while (
            self.portscan_windows[src]
            and self.portscan_windows[src][0].timestamp < cutoff_time
        ):
            old_entry = self.portscan_windows[src].popleft()
            # Remove port from set if no more recent entries
            if old_entry.data not in [e.data for e in self.portscan_windows[src]]:
                self.portscan_ports[src].discard(old_entry.data)

        # Enhanced detection: Check multiple criteria
        unique_ports = len(self.portscan_ports[src])
        total_attempts = len(self.portscan_windows[src])
        
        # Calculate scan rate (ports per second)
        if self.portscan_windows[src]:
            window_duration = ts - self.portscan_windows[src][0].timestamp
            if window_duration > 0:
                scan_rate = unique_ports / window_duration
            else:
                scan_rate = float('inf')
        else:
            scan_rate = 0
            window_duration = 0

        # Enhanced threshold: Check both unique ports and scan rate
        # A port scan typically has high unique ports AND high scan rate
        is_portscan = False
        severity = "WARNING"
        
        if unique_ports >= threshold:
            is_portscan = True
            # Higher severity for faster scans
            if scan_rate > 5.0:  # More than 5 ports per second
                severity = "CRITICAL"
            elif scan_rate > 2.0:  # More than 2 ports per second
                severity = "WARNING"
        
        # Also check for rapid sequential port access (stealth scan)
        if total_attempts >= threshold * 2 and unique_ports >= threshold * 0.7:
            is_portscan = True
            if severity == "WARNING":
                severity = "CRITICAL"

        if is_portscan:
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="PORT_SCAN",
                severity=severity,
                description=f"Port scan detected: {unique_ports} unique ports probed in {window_duration:.1f}s (rate: {scan_rate:.2f} ports/s)",
                meta={
                    "ports_count": unique_ports,
                    "total_attempts": total_attempts,
                    "window_duration": window_duration,
                    "scan_rate": scan_rate
                },
            )
            self.alert_callback(alert)
            # Reset to avoid spam
            self.portscan_windows[src].clear()
            self.portscan_ports[src].clear()

    def _check_syn_flood(self, src: str, flags: str, ts: float) -> None:
        """Check for SYN flood attack with enhanced detection."""
        config = self.signatures.get("syn_flood", {})
        threshold = config.get("syn_threshold", 200)
        window_seconds = config.get("window_seconds", 10)

        # Track SYN packets
        self.syn_flood_windows[src].append(WindowEntry(ts, "SYN"))

        # Clean old entries
        cutoff_time = ts - window_seconds
        while (
            self.syn_flood_windows[src]
            and self.syn_flood_windows[src][0].timestamp < cutoff_time
        ):
            self.syn_flood_windows[src].popleft()

        # Enhanced detection
        syn_count = len(self.syn_flood_windows[src])
        
        if syn_count >= threshold:
            # Calculate actual window duration and rate
            if self.syn_flood_windows[src]:
                actual_duration = ts - self.syn_flood_windows[src][0].timestamp
                syn_rate = syn_count / actual_duration if actual_duration > 0 else syn_count
            else:
                actual_duration = window_seconds
                syn_rate = syn_count / window_seconds
            
            # Determine severity based on rate
            severity = "CRITICAL"
            if syn_rate > 50:  # More than 50 SYN packets per second
                severity = "CRITICAL"
            elif syn_rate > 20:  # More than 20 SYN packets per second
                severity = "WARNING"
            
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="SYN_FLOOD",
                severity=severity,
                description=f"SYN flood detected: {syn_count} SYN packets in {actual_duration:.1f}s (rate: {syn_rate:.1f} pps)",
                meta={
                    "syn_count": syn_count,
                    "window_seconds": actual_duration,
                    "syn_rate": syn_rate
                },
            )
            self.alert_callback(alert)
            # Reset
            self.syn_flood_windows[src].clear()

    def _check_ping_sweep(self, src: str, dst: str, ts: float) -> None:
        """Check for ping sweep attack."""
        config = self.signatures.get("ping_sweep", {})
        threshold = config.get("hosts_threshold", 50)
        window_seconds = config.get("window_seconds", 30)

        # Track ping targets
        self.ping_sweep_windows[src].append(WindowEntry(ts, dst))
        self.ping_sweep_targets[src].add(dst)

        # Clean old entries
        cutoff_time = ts - window_seconds
        while (
            self.ping_sweep_windows[src]
            and self.ping_sweep_windows[src][0].timestamp < cutoff_time
        ):
            old_entry = self.ping_sweep_windows[src].popleft()
            if old_entry.data not in [e.data for e in self.ping_sweep_windows[src]]:
                self.ping_sweep_targets[src].discard(old_entry.data)

        # Check threshold
        unique_targets = len(self.ping_sweep_targets[src])
        if unique_targets >= threshold:
            window_duration = ts - self.ping_sweep_windows[src][0].timestamp if self.ping_sweep_windows[src] else 0
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="PING_SWEEP",
                severity="WARNING",
                description=f"Ping sweep detected: {unique_targets} hosts probed in {window_duration:.1f}s",
                meta={"targets_count": unique_targets, "window_duration": window_duration},
            )
            self.alert_callback(alert)
            # Reset
            self.ping_sweep_windows[src].clear()
            self.ping_sweep_targets[src].clear()

    def _check_suspicious_port(self, src: str, dst: str, dport: int, ts: float) -> None:
        """Check for access to suspicious ports."""
        alert = Alert(
            id=str(uuid.uuid4()),
            ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
            src=src,
            dst=dst,
            rule="SUSPICIOUS_PORT",
            severity="WARNING",
            description=f"Access attempt to suspicious port {dport}",
            meta={"port": dport},
        )
        self.alert_callback(alert)


