"""CLI interface for IDS."""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class CLIInterface:
    """Command-line interface for IDS."""

    def __init__(self):
        """Initialize CLI interface."""
        self.console = Console() if RICH_AVAILABLE else None

    def display_stats(self, stats: Dict[str, Any]) -> None:
        """
        Display statistics.

        Args:
            stats: Statistics dictionary
        """
        if RICH_AVAILABLE and self.console:
            table = Table(title="IDS Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            for key, value in stats.items():
                table.add_row(str(key), str(value))

            self.console.print(table)
        else:
            print("\n=== IDS Statistics ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            print("=" * 20)

    def display_alerts(self, alerts: List[Dict[str, Any]], tail: Optional[int] = None) -> None:
        """
        Display alerts.

        Args:
            alerts: List of alert dictionaries
            tail: Show only last N alerts
        """
        if tail and tail > 0:
            alerts = alerts[-tail:]

        if not alerts:
            print("No alerts found.")
            return

        if RICH_AVAILABLE and self.console:
            table = Table(title="Recent Alerts")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Rule", style="yellow")
            table.add_column("Severity", style="red")
            table.add_column("Source", style="green")
            table.add_column("Description", style="white")

            for alert in alerts:
                table.add_row(
                    alert.get("ts", "N/A"),
                    alert.get("rule", "N/A"),
                    alert.get("severity", "N/A"),
                    alert.get("src", "N/A"),
                    alert.get("description", "N/A")[:50],
                )

            self.console.print(table)
        else:
            print("\n=== Recent Alerts ===")
            for alert in alerts:
                print(f"Timestamp: {alert.get('ts', 'N/A')}")
                print(f"Rule: {alert.get('rule', 'N/A')}")
                print(f"Severity: {alert.get('severity', 'N/A')}")
                print(f"Source: {alert.get('src', 'N/A')}")
                print(f"Description: {alert.get('description', 'N/A')}")
                print("-" * 40)

    def read_alerts_from_log(self, log_path: str, tail: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read alerts from log file.

        Args:
            log_path: Path to alerts log file
            tail: Read only last N lines

        Returns:
            List of alert dictionaries
        """
        log_file = Path(log_path)
        if not log_file.exists():
            return []

        alerts = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if tail and tail > 0:
                    lines = lines[-tail:]

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        # Try to parse as JSON
                        if line.startswith("{"):
                            alert = json.loads(line)
                        else:
                            # Try to extract JSON from log line
                            if "{" in line:
                                json_start = line.find("{")
                                json_str = line[json_start:]
                                alert = json.loads(json_str)
                            else:
                                continue
                        alerts.append(alert)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Error reading alerts log: {e}")

        return alerts


