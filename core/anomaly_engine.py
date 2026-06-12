"""Anomaly detection engine using statistical and ML methods."""

import time
import csv
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from collections import defaultdict, deque
from dataclasses import dataclass

try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import IsolationForest
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from core.alert import Alert


@dataclass
class StatsWindow:
    """Statistical window for anomaly detection."""

    timestamps: deque
    packet_sizes: deque
    packet_count: int


class AnomalyEngine:
    """Anomaly detection engine."""

    def __init__(self, config: Dict[str, Any], alert_callback: Callable[[Alert], None]):
        """
        Initialize anomaly engine.

        Args:
            config: Configuration dictionary
            alert_callback: Callback function for alerts
        """
        self.config = config
        self.alert_callback = alert_callback
        self.anomaly_config = config.get("anomaly", {})

        # Statistical tracking per source IP
        self.stats_windows: Dict[str, StatsWindow] = defaultdict(
            lambda: StatsWindow(deque(), deque(), 0)
        )

        # ML model
        self.model: Optional[Any] = None
        self.use_ml = self.anomaly_config.get("use_ml", False) and ML_AVAILABLE
        self.model_path = Path(self.anomaly_config.get("model_path", "data/datasets/isof_model.joblib"))

        if self.use_ml:
            self._load_or_train_model()

    def _load_or_train_model(self) -> None:
        """Load existing model or train a new one."""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                print(f"Loaded ML model from {self.model_path}")
            except Exception as e:
                print(f"Failed to load model: {e}. Falling back to rule-based detection.")
                self.use_ml = False
        else:
            print("No ML model found. Using rule-based anomaly detection.")
            self.use_ml = False

    def train_model(self, baseline_path: Optional[str] = None) -> None:
        """
        Train IsolationForest model from baseline data.

        Args:
            baseline_path: Path to baseline CSV file
        """
        if not ML_AVAILABLE:
            print("scikit-learn not available. Cannot train model.")
            return

        if baseline_path is None:
            baseline_path = self.anomaly_config.get("baseline_path", "data/datasets/baseline_train.csv")

        baseline_file = Path(baseline_path)
        if not baseline_file.exists():
            print(f"Baseline file not found: {baseline_file}")
            print("Run tools/generate_baseline.py to create baseline data.")
            return

        try:
            df = pd.read_csv(baseline_file)
            # Select features: packet_rate, avg_payload_size, unique_ports
            features = df[["packet_rate", "avg_payload_size", "unique_ports"]].values

            # Train IsolationForest
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.model.fit(features)

            # Save model
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            print(f"Model trained and saved to {self.model_path}")
            self.use_ml = True

        except Exception as e:
            print(f"Failed to train model: {e}")
            self.use_ml = False

    def process_packet(self, packet_record: Dict[str, Any]) -> None:
        """
        Process a packet record for anomaly detection.

        Args:
            packet_record: Parsed packet record
        """
        src = packet_record.get("src")
        payload_size = packet_record.get("payload_size", 0)
        ts = packet_record.get("ts", time.time())

        if not src:
            return

        # Update statistical window
        window = self.stats_windows[src]
        window.timestamps.append(ts)
        window.packet_sizes.append(payload_size)
        window.packet_count += 1

        # Clean old entries (keep last 60 seconds)
        cutoff_time = ts - 60.0
        while window.timestamps and window.timestamps[0] < cutoff_time:
            window.timestamps.popleft()
            window.packet_sizes.popleft()
            window.packet_count -= 1

        # Check for anomalies
        self._check_statistical_anomalies(src, ts)

        if self.use_ml and self.model:
            self._check_ml_anomalies(src, ts)

    def _check_statistical_anomalies(self, src: str, ts: float) -> None:
        """Check for statistical anomalies."""
        window = self.stats_windows[src]
        if window.packet_count < 10:  # Need minimum samples
            return

        # Calculate packet rate (per minute) with enhanced precision
        if window.timestamps and len(window.timestamps) > 1:
            time_span = window.timestamps[-1] - window.timestamps[0]
            if time_span > 0:
                # More accurate: use actual packet count in window
                actual_packet_count = len(window.timestamps)
                packet_rate = (actual_packet_count / time_span) * 60.0
            else:
                packet_rate = 0
        else:
            packet_rate = 0

        # Calculate average payload size
        if window.packet_sizes:
            avg_payload_size = sum(window.packet_sizes) / len(window.packet_sizes)
        else:
            avg_payload_size = 0

        # Check thresholds
        rate_threshold = self.anomaly_config.get("packet_rate_threshold", 1000)
        payload_threshold = self.anomaly_config.get("payload_size_threshold_bytes", 10000)

        if packet_rate > rate_threshold:
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="ANOMALY_HIGH_RATE",
                severity="WARNING",
                description=f"Unusually high packet rate: {packet_rate:.1f} packets/min",
                meta={"packet_rate": packet_rate, "threshold": rate_threshold},
            )
            self.alert_callback(alert)

        if avg_payload_size > payload_threshold:
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="ANOMALY_LARGE_PAYLOAD",
                severity="INFO",
                description=f"Unusually large average payload: {avg_payload_size:.0f} bytes",
                meta={"avg_payload_size": avg_payload_size, "threshold": payload_threshold},
            )
            self.alert_callback(alert)

    def _check_ml_anomalies(self, src: str, ts: float) -> None:
        """Check for ML-based anomalies."""
        if not self.model:
            return

        window = self.stats_windows[src]
        if window.packet_count < 10:
            return

        # Calculate features
        if window.timestamps:
            time_span = window.timestamps[-1] - window.timestamps[0]
            packet_rate = (window.packet_count / time_span) * 60.0 if time_span > 0 else 0
        else:
            packet_rate = 0

        if window.packet_sizes:
            avg_payload_size = sum(window.packet_sizes) / len(window.packet_sizes)
        else:
            avg_payload_size = 0

        # For unique ports, we'd need to track that separately
        # For now, use a placeholder
        unique_ports = 1  # Simplified

        # Predict anomaly
        features = np.array([[packet_rate, avg_payload_size, unique_ports]])
        prediction = self.model.predict(features)

        if prediction[0] == -1:  # Anomaly detected
            alert = Alert(
                id=str(uuid.uuid4()),
                ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                src=src,
                dst="multiple",
                rule="ANOMALY_ML",
                severity="WARNING",
                description="ML model detected anomalous traffic pattern",
                meta={
                    "packet_rate": packet_rate,
                    "avg_payload_size": avg_payload_size,
                    "unique_ports": unique_ports,
                },
            )
            self.alert_callback(alert)