#!/usr/bin/env python3
"""PCAP file generator for testing IDS."""

import argparse
import random
import time
from pathlib import Path
from scapy.all import IP, TCP, UDP, ICMP, Raw, wrpcap, RandIP, RandShort


def generate_benign_traffic(count: int = 100) -> list:
    """
    Generate benign network traffic packets.

    Args:
        count: Number of packets to generate

    Returns:
        List of Scapy packets
    """
    packets = []
    base_time = time.time()

    # Common ports for benign traffic
    common_ports = [80, 443, 53, 22, 25, 110, 143, 993, 995]

    for i in range(count):
        src_ip = f"192.168.1.{random.randint(1, 50)}"
        dst_ip = f"192.168.1.{random.randint(51, 100)}"
        dst_port = random.choice(common_ports)

        # Mix of TCP, UDP, and ICMP
        protocol = random.choice(["TCP", "UDP", "ICMP"])

        if protocol == "TCP":
            packet = IP(src=src_ip, dst=dst_ip) / TCP(
                sport=RandShort(), dport=dst_port, flags="SA"
            )
        elif protocol == "UDP":
            packet = IP(src=src_ip, dst=dst_ip) / UDP(sport=RandShort(), dport=dst_port)
        else:  # ICMP
            packet = IP(src=src_ip, dst=dst_ip) / ICMP()

        packet.time = base_time + i * 0.1
        packets.append(packet)

    return packets


def generate_port_scan_traffic(attacker_ip: str, target_ip: str, port_count: int = 25) -> list:
    """
    Generate port scan traffic.

    Args:
        attacker_ip: Attacker source IP
        target_ip: Target IP
        port_count: Number of ports to scan

    Returns:
        List of Scapy packets
    """
    packets = []
    base_time = time.time()

    for i in range(port_count):
        port = random.randint(1, 65535)
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(), dport=port, flags="S"
        )
        packet.time = base_time + i * 0.05  # Fast scan
        packets.append(packet)

    return packets


def generate_syn_flood_traffic(attacker_ip: str, target_ip: str, target_port: int, count: int = 200) -> list:
    """
    Generate SYN flood traffic.

    Args:
        attacker_ip: Attacker source IP
        target_ip: Target IP
        target_port: Target port
        count: Number of SYN packets

    Returns:
        List of Scapy packets
    """
    packets = []
    base_time = time.time()

    for i in range(count):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(), dport=target_port, flags="S"
        )
        packet.time = base_time + i * 0.01  # Very fast
        packets.append(packet)

    return packets


def generate_ping_sweep_traffic(attacker_ip: str, network_base: str, host_count: int = 50) -> list:
    """
    Generate ping sweep traffic.

    Args:
        attacker_ip: Attacker source IP
        network_base: Network base (e.g., "192.168.1")
        host_count: Number of hosts to ping

    Returns:
        List of Scapy packets
    """
    packets = []
    base_time = time.time()

    for i in range(host_count):
        host = random.randint(1, 254)
        target_ip = f"{network_base}.{host}"
        packet = IP(src=attacker_ip, dst=target_ip) / ICMP(type=8)  # Echo request
        packet.time = base_time + i * 0.1
        packets.append(packet)

    return packets


def generate_sample_pcap(output_path: str) -> None:
    """
    Generate a sample PCAP file with mixed traffic.

    Args:
        output_path: Output PCAP file path
    """
    print("Generating sample PCAP file...")

    all_packets = []

    # Add benign traffic
    print("  - Generating benign traffic...")
    all_packets.extend(generate_benign_traffic(100))

    # Add port scan
    print("  - Generating port scan traffic...")
    all_packets.extend(generate_port_scan_traffic("192.168.1.14", "192.168.1.5", 25))

    # Add SYN flood
    print("  - Generating SYN flood traffic...")
    all_packets.extend(generate_syn_flood_traffic("192.168.1.15", "192.168.1.5", 80, 200))

    # Add ping sweep
    print("  - Generating ping sweep traffic...")
    all_packets.extend(generate_ping_sweep_traffic("192.168.1.16", "192.168.1", 50))

    # Sort by timestamp
    all_packets.sort(key=lambda p: p.time)

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output_file), all_packets)

    print(f"Generated {len(all_packets)} packets in {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate PCAP files for IDS testing")
    parser.add_argument(
        "--output",
        default="data/pcap_samples/sample_traffic.pcap",
        help="Output PCAP file path",
    )
    parser.add_argument(
        "--benign-count",
        type=int,
        default=100,
        help="Number of benign packets",
    )
    parser.add_argument(
        "--portscan-ports",
        type=int,
        default=25,
        help="Number of ports in port scan",
    )
    parser.add_argument(
        "--synflood-count",
        type=int,
        default=200,
        help="Number of SYN packets",
    )
    parser.add_argument(
        "--pingsweep-hosts",
        type=int,
        default=50,
        help="Number of hosts in ping sweep",
    )

    args = parser.parse_args()

    generate_sample_pcap(args.output)


if __name__ == "__main__":
    main()


