"""Alert module for IDS."""

import uuid
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    try:
        from colorama import init, Fore, Style
        init()
        COLORAMA_AVAILABLE = True
    except ImportError:
        COLORAMA_AVAILABLE = False

from core.utils import get_iso_timestamp


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    ts: str
    src: str
    dst: str
    rule: str
    severity: str  # INFO, WARNING, CRITICAL
    description: str
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "ts": self.ts,
            "src": self.src,
            "dst": self.dst,
            "rule": self.rule,
            "severity": self.severity,
            "description": self.description,
            "meta": self.meta,
        }

    def to_json(self) -> str:
        """Convert alert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AlertManager:
    """Manages alert display and forwarding."""

    def __init__(self, console_output: bool = True, json_output: bool = False):
        """
        Initialize alert manager.

        Args:
            console_output: Enable console output
            json_output: Enable JSON output to stdout
        """
        self.console_output = console_output
        self.json_output = json_output
        self.console = Console() if RICH_AVAILABLE else None

    def display_alert(self, alert: Alert) -> None:
        """
        Display alert to console.

        Args:
            alert: Alert object to display
        """
        if self.json_output:
            print(alert.to_json())
            return

        if not self.console_output:
            return

        if RICH_AVAILABLE and self.console:
            self._display_rich(alert)
        elif COLORAMA_AVAILABLE:
            self._display_colorama(alert)
        else:
            self._display_plain(alert)

    def _display_rich(self, alert: Alert) -> None:
        """Display alert using rich library."""
        severity_colors = {
            "INFO": "blue",
            "WARNING": "yellow",
            "CRITICAL": "red",
        }
        color = severity_colors.get(alert.severity, "white")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style=color)

        table.add_row("ID", alert.id)
        table.add_row("Timestamp", alert.ts)
        table.add_row("Source", alert.src)
        table.add_row("Destination", alert.dst)
        table.add_row("Rule", alert.rule)
        table.add_row("Severity", alert.severity)
        table.add_row("Description", alert.description)
        if alert.meta:
            table.add_row("Metadata", json.dumps(alert.meta, indent=2))

        panel = Panel(table, title=f"[{color}]ALERT: {alert.rule}[/{color}]", border_style=color)
        self.console.print(panel)

    def _display_colorama(self, alert: Alert) -> None:
        """Display alert using colorama."""
        severity_colors = {
            "INFO": Fore.BLUE,
            "WARNING": Fore.YELLOW,
            "CRITICAL": Fore.RED,
        }
        color = severity_colors.get(alert.severity, Fore.WHITE)

        print(f"\n{color}{'='*60}{Style.RESET_ALL}")
        print(f"{color}ALERT: {alert.rule}{Style.RESET_ALL}")
        print(f"{color}{'='*60}{Style.RESET_ALL}")
        print(f"ID: {alert.id}")
        print(f"Timestamp: {alert.ts}")
        print(f"Source: {alert.src}")
        print(f"Destination: {alert.dst}")
        print(f"Severity: {color}{alert.severity}{Style.RESET_ALL}")
        print(f"Description: {alert.description}")
        if alert.meta:
            print(f"Metadata: {json.dumps(alert.meta, indent=2)}")
        print(f"{color}{'='*60}{Style.RESET_ALL}\n")

    def _display_plain(self, alert: Alert) -> None:
        """Display alert in plain text."""
        print(f"\n{'='*60}")
        print(f"ALERT: {alert.rule}")
        print(f"{'='*60}")
        print(f"ID: {alert.id}")
        print(f"Timestamp: {alert.ts}")
        print(f"Source: {alert.src}")
        print(f"Destination: {alert.dst}")
        print(f"Severity: {alert.severity}")
        print(f"Description: {alert.description}")
        if alert.meta:
            print(f"Metadata: {json.dumps(alert.meta, indent=2)}")
        print(f"{'='*60}\n")

    def create_alert(
        self,
        src: str,
        dst: str,
        rule: str,
        severity: str,
        description: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """
        Create a new alert.

        Args:
            src: Source IP
            dst: Destination IP
            rule: Rule name that triggered
            severity: Alert severity
            description: Alert description
            meta: Optional metadata

        Returns:
            Alert object
        """
        return Alert(
            id=str(uuid.uuid4()),
            ts=get_iso_timestamp(),
            src=src,
            dst=dst,
            rule=rule,
            severity=severity,
            description=description,
            meta=meta or {},
        )

    # Placeholder methods for future integrations
    def send_email(self, alert: Alert, recipients: list) -> None:
        """Placeholder for email alerting."""
        pass

    def send_webhook(self, alert: Alert, webhook_url: str) -> None:
        """Placeholder for webhook alerting."""
        pass