#!/usr/bin/env python3
"""Generate example PCAP files for testing IDS."""

import argparse
import random
import time
from pathlib import Path
from scapy.all import IP, TCP, UDP, ICMP, Raw, wrpcap, RandIP, RandShort

def generate_benign_traffic(count: int = 100) -> list:
    """Generate benign network traffic packets."""
    packets = []
    base_time = time.time()

    common_ports = [80, 443, 53, 22, 25, 110, 143, 993, 995]

    for i in range(count):
        src_ip = f"192.168.1.{random.randint(1, 50)}"
        dst_ip = f"192.168.1.{random.randint(51, 100)}"
        dst_port = random.choice(common_ports)

        protocol = random.choice(["TCP", "UDP", "ICMP"])

        if protocol == "TCP":
            packet = IP(src=src_ip, dst=dst_ip) / TCP(
                sport=RandShort(), dport=dst_port, flags="SA"
            )
        elif protocol == "UDP":
            packet = IP(src=src_ip, dst=dst_ip) / UDP(sport=RandShort(), dport=dst_port)
        else:
            packet = IP(src=src_ip, dst=dst_ip) / ICMP()

        packet.time = base_time + i * 0.1
        packets.append(packet)

    return packets

def generate_port_scan(attacker_ip: str, target_ip: str, port_count: int = 30) -> list:
    """Generate port scan traffic."""
    packets = []
    base_time = time.time()

    for i in range(port_count):
        port = random.randint(1, 65535)
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(), dport=port, flags="S"
        )
        packet.time = base_time + i * 0.05
        packets.append(packet)

    return packets

def generate_syn_flood(attacker_ip: str, target_ip: str, target_port: int, count: int = 250) -> list:
    """Generate SYN flood traffic."""
    packets = []
    base_time = time.time()

    for i in range(count):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(), dport=target_port, flags="S"
        )
        packet.time = base_time + i * 0.01
        packets.append(packet)

    return packets

def generate_ping_sweep(attacker_ip: str, network_base: str, host_count: int = 60) -> list:
    """Generate ping sweep traffic."""
    packets = []
    base_time = time.time()

    for i in range(host_count):
        host = random.randint(1, 254)
        target_ip = f"{network_base}.{host}"
        packet = IP(src=attacker_ip, dst=target_ip) / ICMP(type=8)
        packet.time = base_time + i * 0.1
        packets.append(packet)

    return packets

def generate_suspicious_ports(attacker_ip: str, target_ip: str) -> list:
    """Generate traffic to suspicious ports."""
    packets = []
    base_time = time.time()
    suspicious_ports = [21, 22, 23, 3389, 4444, 6667, 31337]

    for i, port in enumerate(suspicious_ports):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(), dport=port, flags="S"
        )
        packet.time = base_time + i * 0.2
        packets.append(packet)

    return packets

def generate_mixed_attack(attacker_ip: str, target_ip: str) -> list:
    """Generate mixed attack traffic."""
    packets = []
    base_time = time.time()

    # Port scan
    packets.extend(generate_port_scan(attacker_ip, target_ip, 25))
    
    # SYN flood
    packets.extend(generate_syn_flood(attacker_ip, target_ip, 80, 200))
    
    # Ping sweep
    packets.extend(generate_ping_sweep(attacker_ip, "192.168.1", 50))
    
    # Suspicious ports
    packets.extend(generate_suspicious_ports(attacker_ip, target_ip))

    # Sort by timestamp
    packets.sort(key=lambda p: p.time)
    return packets

def main():
    """Generate example PCAP files."""
    parser = argparse.ArgumentParser(description="Generate example PCAP files for IDS testing")
    parser.add_argument(
        "--output-dir",
        default="data/pcap_samples",
        help="Output directory for PCAP files",
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generation de fichiers PCAP d'exemple")
    print("=" * 60)
    print()

    # 1. Trafic benin
    print("1. Generation: trafic_benin.pcap")
    packets = generate_benign_traffic(150)
    output_file = output_dir / "trafic_benin.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 2. Port scan
    print("2. Generation: port_scan.pcap")
    packets = generate_port_scan("192.168.1.100", "192.168.1.5", 30)
    output_file = output_dir / "port_scan.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 3. SYN flood
    print("3. Generation: syn_flood.pcap")
    packets = generate_syn_flood("192.168.1.101", "192.168.1.5", 80, 250)
    output_file = output_dir / "syn_flood.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 4. Ping sweep
    print("4. Generation: ping_sweep.pcap")
    packets = generate_ping_sweep("192.168.1.102", "192.168.1", 60)
    output_file = output_dir / "ping_sweep.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 5. Ports suspects
    print("5. Generation: ports_suspects.pcap")
    packets = generate_suspicious_ports("192.168.1.103", "192.168.1.5")
    output_file = output_dir / "ports_suspects.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 6. Attaque mixte
    print("6. Generation: attaque_mixte.pcap")
    packets = generate_mixed_attack("192.168.1.104", "192.168.1.5")
    output_file = output_dir / "attaque_mixte.pcap"
    wrpcap(str(output_file), packets)
    print(f"   [+] {len(packets)} paquets generes -> {output_file}")
    print()

    # 7. Trafic mixte (benin + attaques)
    print("7. Generation: trafic_mixte.pcap")
    all_packets = []
    all_packets.extend(generate_benign_traffic(100))
    all_packets.extend(generate_port_scan("192.168.1.105", "192.168.1.5", 25))
    all_packets.extend(generate_syn_flood("192.168.1.106", "192.168.1.5", 80, 200))
    all_packets.sort(key=lambda p: p.time)
    output_file = output_dir / "trafic_mixte.pcap"
    wrpcap(str(output_file), all_packets)
    print(f"   [+] {len(all_packets)} paquets generes -> {output_file}")
    print()

    print("=" * 60)
    print("[+] Tous les fichiers d'exemple ont ete generes avec succes!")
    print(f"  Dossier: {output_dir.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    main()

