#!/usr/bin/env python3
"""Generate baseline training dataset for ML anomaly detection."""

import argparse
import csv
import random
from pathlib import Path


def generate_baseline_csv(output_path: str, num_samples: int = 1000) -> None:
    """
    Generate baseline CSV dataset for ML training.

    Args:
        output_path: Output CSV file path
        num_samples: Number of samples to generate
    """
    print(f"Generating baseline dataset with {num_samples} samples...")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["packet_rate", "avg_payload_size", "unique_ports"])

        for _ in range(num_samples):
            # Generate normal traffic patterns
            packet_rate = random.uniform(10, 500)  # Normal: 10-500 packets/min
            avg_payload_size = random.uniform(100, 2000)  # Normal: 100-2000 bytes
            unique_ports = random.randint(1, 20)  # Normal: 1-20 unique ports

            writer.writerow([packet_rate, avg_payload_size, unique_ports])

    print(f"Baseline dataset saved to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate baseline training dataset")
    parser.add_argument(
        "--output",
        default="data/datasets/baseline_train.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=1000,
        help="Number of samples to generate",
    )

    args = parser.parse_args()
    generate_baseline_csv(args.output, args.samples)


if __name__ == "__main__":
    main()


