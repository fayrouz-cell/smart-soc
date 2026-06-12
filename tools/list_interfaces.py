#!/usr/bin/env python3
"""List available network interfaces for packet capture."""

import sys
import platform
from scapy.all import get_if_list, get_if_addr, get_if_raw_hwaddr

def list_interfaces():
    """List all available network interfaces with details."""
    print("=" * 60)
    print("Interfaces réseau disponibles pour la capture")
    print("=" * 60)
    print()
    
    try:
        interfaces = get_if_list()
        
        if not interfaces:
            print("❌ Aucune interface réseau trouvée.")
            print("\nNote: Sur Windows, vous devez installer Npcap ou WinPcap")
            print("Téléchargez Npcap depuis: https://nmap.org/npcap/")
            return
        
        print(f"✅ {len(interfaces)} interface(s) trouvée(s):\n")
        
        for i, iface in enumerate(interfaces, 1):
            try:
                addr = get_if_addr(iface)
                hwaddr = get_if_raw_hwaddr(iface)
                hwaddr_str = ":".join(f"{b:02x}" for b in hwaddr[1]) if hwaddr[1] else "N/A"
                
                # Détecter le type d'interface
                iface_type = "?"
                iface_lower = iface.lower()
                if "wi" in iface_lower or "wlan" in iface_lower or "wireless" in iface_lower:
                    iface_type = "📶 WiFi"
                elif "eth" in iface_lower or "ethernet" in iface_lower:
                    iface_type = "🔌 Ethernet"
                elif "lo" in iface_lower or "loopback" in iface_lower:
                    iface_type = "🔁 Loopback"
                else:
                    iface_type = "🌐 Autre"
                
                print(f"{i}. {iface_type} - {iface}")
                print(f"   Adresse IP: {addr if addr else 'Non configurée'}")
                print(f"   Adresse MAC: {hwaddr_str}")
                print()
                
            except Exception as e:
                print(f"{i}. {iface} (erreur: {e})")
                print()
        
        print("=" * 60)
        print("\n💡 Pour scanner votre WiFi Oreedo:")
        print("   1. Identifiez l'interface WiFi dans la liste ci-dessus")
        print("   2. Utilisez la commande suivante (en tant qu'administrateur):")
        print()
        
        # Trouver l'interface WiFi
        wifi_iface = None
        for iface in interfaces:
            iface_lower = iface.lower()
            if "wi" in iface_lower or "wlan" in iface_lower or "wireless" in iface_lower:
                wifi_iface = iface
                break
        
        if wifi_iface:
            print(f"   python main.py --start --mode live --interface {wifi_iface}")
        else:
            print("   python main.py --start --mode live --interface <NOM_INTERFACE>")
        
        print()
        print("⚠️  IMPORTANT: Sur Windows, vous devez:")
        print("   - Exécuter en tant qu'administrateur (clic droit > Exécuter en tant qu'administrateur)")
        print("   - Avoir installé Npcap (https://nmap.org/npcap/)")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de la liste des interfaces: {e}")
        print("\nVérifiez que Scapy est correctement installé:")
        print("   pip install scapy")
        
        if platform.system() == "Windows":
            print("\nSur Windows, installez également Npcap:")
            print("   https://nmap.org/npcap/")
        
        sys.exit(1)


if __name__ == "__main__":
    list_interfaces()

