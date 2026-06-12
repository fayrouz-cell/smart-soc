#!/usr/bin/env python3
"""
Génération d'un fichier PCAP de test complet pour tester l'IDS.
Contient tous les types d'attaques et anomalies pour validation complète.
"""

import argparse
import random
import time
from pathlib import Path
from scapy.all import IP, TCP, UDP, ICMP, Raw, wrpcap, RandShort


def generate_port_scan(attacker_ip: str, target_ip: str, ports: list) -> list:
    """
    Génère des paquets pour simuler un scan de ports.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        ports: Liste des ports à scanner
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [Port Scan] Génération de {len(ports)} paquets SYN vers {target_ip}")
    
    for i, port in enumerate(ports):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=port,
            flags="S"  # SYN flag
        )
        packet.time = base_time + i * 0.05  # Scan rapide
        packets.append(packet)
    
    return packets


def generate_syn_flood(attacker_ip: str, target_ip: str, target_port: int, count: int = 250) -> list:
    """
    Génère des paquets pour simuler une attaque SYN Flood.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        target_port: Port cible
        count: Nombre de paquets SYN
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [SYN Flood] Generation de {count} paquets SYN vers {target_ip}:{target_port}")
    
    for i in range(count):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=target_port,
            flags="S"  # SYN flag
        )
        packet.time = base_time + i * 0.01  # Très rapide pour simuler un flood
        packets.append(packet)
    
    return packets


def generate_ping_sweep(attacker_ip: str, network_base: str, host_range: list) -> list:
    """
    Génère des paquets ICMP pour simuler un ping sweep.
    
    Args:
        attacker_ip: IP de l'attaquant
        network_base: Base du réseau (ex: "192.168.1")
        host_range: Liste des hôtes à scanner
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [Ping Sweep] Generation de {len(host_range)} paquets ICMP vers {len(host_range)} hotes")
    
    for i, host in enumerate(host_range):
        target_ip = f"{network_base}.{host}"
        packet = IP(src=attacker_ip, dst=target_ip) / ICMP(type=8, code=0)  # Echo Request
        packet.time = base_time + i * 0.1
        packets.append(packet)
    
    return packets


def generate_suspicious_ports(attacker_ip: str, target_ip: str, suspicious_ports: list) -> list:
    """
    Génère des paquets vers des ports suspects.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        suspicious_ports: Liste des ports suspects
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [Ports Suspects] Generation de paquets vers {len(suspicious_ports)} ports suspects")
    
    for i, port in enumerate(suspicious_ports):
        # Mix de SYN et ACK pour varier
        flags = "S" if i % 2 == 0 else "A"
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=port,
            flags=flags
        )
        packet.time = base_time + i * 0.2
        packets.append(packet)
    
    return packets


def generate_high_rate_anomaly(attacker_ip: str, target_ip: str, target_port: int, count: int = 500) -> list:
    """
    Génère un grand nombre de paquets rapidement pour simuler une anomalie de taux élevé.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        target_port: Port cible
        count: Nombre de paquets
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [Anomalie Taux Eleve] Generation de {count} paquets a taux eleve vers {target_ip}:{target_port}")
    
    # Générer des paquets très rapidement
    for i in range(count):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=target_port,
            flags="S"
        )
        packet.time = base_time + i * 0.005  # Très rapide (200 paquets/seconde)
        packets.append(packet)
    
    return packets


def generate_large_payload_anomaly(attacker_ip: str, target_ip: str, target_port: int, payload_size_kb: float = 50.0) -> list:
    """
    Génère des paquets avec des charges utiles très grandes.
    Note: TCP limite la taille à ~65535 bytes par paquet, donc on génère plusieurs paquets.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        target_port: Port cible
        payload_size_kb: Taille totale du payload en Ko (divisé en plusieurs paquets)
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    # Limite TCP par paquet (moins headers IP/TCP)
    max_payload_per_packet = 60000  # ~60 KB par paquet pour être sûr
    total_payload_size = int(payload_size_kb * 1024)  # Convertir en bytes
    num_packets = (total_payload_size + max_payload_per_packet - 1) // max_payload_per_packet
    
    print(f"  [Anomalie Payload Large] Generation de {num_packets} paquets avec payload total de {payload_size_kb} Ko")
    
    # Générer plusieurs paquets avec de gros payloads
    for i in range(num_packets):
        # Calculer la taille du payload pour ce paquet
        if i == num_packets - 1:
            # Dernier paquet: reste du payload
            packet_payload_size = total_payload_size - (i * max_payload_per_packet)
        else:
            packet_payload_size = max_payload_per_packet
        
        payload = b"X" * packet_payload_size
        
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=target_port,
            flags="PA",  # PSH + ACK
            seq=i * max_payload_per_packet
        ) / Raw(load=payload)
        
        packet.time = base_time + i * 0.01
        packets.append(packet)
    
    return packets


def generate_ml_anomaly(attacker_ip: str, target_ip: str) -> list:
    """
    Génère une combinaison d'attaques pour simuler une anomalie ML.
    Combine Port Scan + SYN Flood pour créer un comportement anormal.
    
    Args:
        attacker_ip: IP de l'attaquant
        target_ip: IP cible
        
    Returns:
        Liste de paquets Scapy
    """
    packets = []
    base_time = time.time()
    
    print(f"  [Anomalie ML] Generation d'une combinaison d'attaques (Port Scan + SYN Flood)")
    
    # Port Scan vers plusieurs ports
    scan_ports = [80, 443, 22, 21, 25, 53, 3389, 445, 8080, 8443]
    for i, port in enumerate(scan_ports):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=port,
            flags="S"
        )
        packet.time = base_time + i * 0.05
        packets.append(packet)
    
    # SYN Flood vers le port 80
    for i in range(150):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=80,
            flags="S"
        )
        packet.time = base_time + len(scan_ports) * 0.05 + i * 0.01
        packets.append(packet)
    
    # SYN Flood vers le port 22 (SSH)
    for i in range(100):
        packet = IP(src=attacker_ip, dst=target_ip) / TCP(
            sport=RandShort(),
            dport=22,
            flags="S"
        )
        packet.time = base_time + len(scan_ports) * 0.05 + 150 * 0.01 + i * 0.01
        packets.append(packet)
    
    return packets


def generate_test_pcap(output_path: str) -> None:
    """
    Génère un fichier PCAP de test complet avec tous les types d'attaques.
    
    Args:
        output_path: Chemin du fichier PCAP de sortie
    """
    print("=" * 70)
    print("GENERATION DU FICHIER PCAP DE TEST POUR IDS")
    print("=" * 70)
    print()
    
    all_packets = []
    attacker_ip = "192.168.1.10"
    target_ip = "192.168.1.10"
    base_time = time.time()
    
    # 1. PORT SCAN
    print("1. Port Scan")
    scan_ports = [80, 443, 22, 21, 25, 53, 8080, 8443, 3306, 5432, 27017, 6379, 9200, 5601, 3000, 5000, 8000, 9000, 3389, 445, 23, 110, 143, 993, 995]
    all_packets.extend(generate_port_scan(attacker_ip, target_ip, scan_ports))
    print(f"   [+] {len(scan_ports)} paquets generes\n")
    
    # 2. SYN FLOOD
    print("2. SYN Flood")
    all_packets.extend(generate_syn_flood(attacker_ip, target_ip, 80, 250))
    print(f"   [+] 250 paquets SYN generes\n")
    
    # 3. PING SWEEP
    print("3. Ping Sweep")
    host_range = list(range(1, 21))  # 192.168.1.1 à 192.168.1.20
    all_packets.extend(generate_ping_sweep(attacker_ip, "192.168.1", host_range))
    print(f"   [+] {len(host_range)} paquets ICMP generes\n")
    
    # 4. PORTS SUSPECTS
    print("4. Ports Suspects")
    suspicious_ports = [22, 3389, 445, 21, 23, 4444, 6667]  # SSH, RDP, SMB, FTP, Telnet, Backdoor, IRC
    all_packets.extend(generate_suspicious_ports(attacker_ip, target_ip, suspicious_ports))
    print(f"   [+] {len(suspicious_ports)} paquets vers ports suspects generes\n")
    
    # 5. ANOMALIE - TAUX ÉLEVÉ
    print("5. Anomalie - Taux Élevé")
    all_packets.extend(generate_high_rate_anomaly(attacker_ip, target_ip, 80, 500))
    print(f"   [+] 500 paquets a taux eleve generes\n")
    
    # 6. ANOMALIE - PAYLOAD LARGE
    print("6. Anomalie - Payload Large")
    large_payload_packets = generate_large_payload_anomaly(attacker_ip, target_ip, 80, 50.0)  # 50 Ko total
    all_packets.extend(large_payload_packets)
    print(f"   [+] {len(large_payload_packets)} paquet(s) avec payload large (50 Ko total) genere(s)\n")
    
    # 7. ANOMALIE ML (Combinaison d'attaques)
    print("7. Anomalie ML (Combinaison d'attaques)")
    ml_packets = generate_ml_anomaly(attacker_ip, target_ip)
    all_packets.extend(ml_packets)
    print(f"   [+] {len(ml_packets)} paquets combines generes\n")
    
    # Ajouter quelques paquets bénins pour contexte
    print("8. Trafic Bénin (contexte)")
    benign_count = 50
    for i in range(benign_count):
        src_ip = f"192.168.1.{random.randint(1, 9)}"
        dst_ip = f"192.168.1.{random.randint(11, 20)}"
        dst_port = random.choice([80, 443, 53])
        
        packet = IP(src=src_ip, dst=dst_ip) / TCP(
            sport=RandShort(),
            dport=dst_port,
            flags="SA"  # SYN + ACK (connexion établie)
        )
        packet.time = base_time + i * 0.5
        all_packets.append(packet)
    print(f"   [+] {benign_count} paquets benins generes\n")
    
    # Trier tous les paquets par timestamp
    print("Tri des paquets par timestamp...")
    all_packets.sort(key=lambda p: p.time)
    
    # Écrire dans le fichier
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Écriture de {len(all_packets)} paquets dans {output_file}...")
    wrpcap(str(output_file), all_packets)
    
    # Calculer la taille du fichier
    file_size = output_file.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print()
    print("=" * 70)
    print("GENERATION TERMINEE")
    print("=" * 70)
    print(f"Fichier genere: {output_file}")
    print(f"Nombre de paquets: {len(all_packets)}")
    print(f"Taille du fichier: {file_size_mb:.2f} Mo ({file_size:,} bytes)")
    print()
    print("Types d'attaques inclus:")
    print("  [+] Port Scan (25 ports)")
    print("  [+] SYN Flood (250 paquets)")
    print("  [+] Ping Sweep (20 hotes)")
    print("  [+] Ports Suspects (7 ports)")
    print("  [+] Anomalie - Taux Eleve (500 paquets)")
    print("  [+] Anomalie - Payload Large (50 Ko)")
    print("  [+] Anomalie ML (combinaison d'attaques)")
    print("  [+] Trafic Benin (50 paquets)")
    print()
    print("Pour tester l'IDS:")
    print(f"  1. Utilisez le mode 'Replay PCAP' dans le dashboard")
    print(f"  2. Sélectionnez le fichier: {output_file}")
    print(f"  3. Démarrez l'IDS et observez les alertes générées")
    print("=" * 70)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Genere un fichier PCAP de test complet pour l'IDS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python tools/generate_test_pcap.py
  python tools/generate_test_pcap.py --output data/pcap_samples/test_pcap_file.pcap
  python tools/generate_test_pcap.py --output test.pcap
        """
    )
    parser.add_argument(
        "--output",
        default="data/pcap_samples/test_pcap_file.pcap",
        help="Chemin du fichier PCAP de sortie (defaut: data/pcap_samples/test_pcap_file.pcap)",
    )
    
    args = parser.parse_args()
    
    try:
        generate_test_pcap(args.output)
    except Exception as e:
        print(f"ERREUR lors de la generation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

