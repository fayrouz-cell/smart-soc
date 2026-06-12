# Guide d'utilisation du fichier PCAP de test

## 📋 Vue d'ensemble

Le fichier `test_pcap_file.pcap` contient un ensemble complet de paquets réseau simulés pour tester toutes les fonctionnalités de détection de l'IDS.

## 📁 Fichier généré

- **Chemin**: `data/pcap_samples/test_pcap_file.pcap`
- **Taille**: ~63 KB
- **Nombre de paquets**: 1113
- **Script de génération**: `tools/generate_test_pcap.py`

## 🎯 Types d'attaques inclus

### 1. Port Scan (25 ports)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10
- **Ports scannés**: 80, 443, 22, 21, 25, 53, 8080, 8443, 3306, 5432, 27017, 6379, 9200, 5601, 3000, 5000, 8000, 9000, 3389, 445, 23, 110, 143, 993, 995
- **Type**: Paquets SYN
- **Résultat attendu**: Alerte **PORT_SCAN** (détection de scan sur 20+ ports)

### 2. SYN Flood (250 paquets)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10:80
- **Type**: 250 paquets SYN envoyés rapidement
- **Résultat attendu**: Alerte **SYN_FLOOD** (détection de >200 SYN en 10 secondes)

### 3. Ping Sweep (20 hôtes)
- **Source**: 192.168.1.10
- **Destinations**: 192.168.1.1 à 192.168.1.20
- **Type**: Paquets ICMP Echo Request
- **Résultat attendu**: Alerte **PING_SWEEP** (détection de >50 hôtes en 30 secondes)

### 4. Ports Suspects (7 ports)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10
- **Ports**: 22 (SSH), 3389 (RDP), 445 (SMB), 21 (FTP), 23 (Telnet), 4444 (Backdoor), 6667 (IRC)
- **Type**: Paquets SYN et ACK
- **Résultat attendu**: Alertes **SUSPICIOUS_PORT** pour chaque port suspect

### 5. Anomalie - Taux Élevé (500 paquets)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10:80
- **Type**: 500 paquets SYN envoyés très rapidement (200 pkt/sec)
- **Résultat attendu**: Alerte **ANOMALY** - Taux de paquets élevé (>3000 paquets/min)

### 6. Anomalie - Payload Large (50 Ko)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10:80
- **Type**: Paquet(s) TCP avec payload de 50 Ko
- **Résultat attendu**: Alerte **ANOMALY** - Payload size threshold (>10000 bytes)

### 7. Anomalie ML (Combinaison d'attaques)
- **Source**: 192.168.1.10
- **Destination**: 192.168.1.10
- **Type**: Combinaison de Port Scan (10 ports) + SYN Flood (150 paquets vers port 80) + SYN Flood (100 paquets vers port 22)
- **Résultat attendu**: Alertes multiples combinées pouvant déclencher une détection ML

### 8. Trafic Bénin (50 paquets)
- **Type**: Trafic normal pour contexte
- **Résultat attendu**: Aucune alerte

## 🚀 Comment utiliser le fichier PCAP

### Méthode 1: Via le Dashboard Web

1. **Démarrer l'application web**:
   ```bash
   python web/run_web.py
   # ou
   python -m web.run_web
   ```

2. **Accéder au dashboard**:
   - Ouvrir `http://localhost:5000/dashboard`
   - Se connecter (admin/admin123 ou user/user123)

3. **Charger le fichier PCAP**:
   - Sélectionner le mode **"Replay (PCAP)"**
   - Entrer le chemin: `data/pcap_samples/test_pcap_file.pcap`
   - Ou utiliser le bouton **"Upload PCAP"** pour téléverser le fichier

4. **Démarrer l'IDS**:
   - Cliquer sur **"Démarrer IDS"**
   - Observer les alertes en temps réel dans le dashboard

### Méthode 2: Via la ligne de commande

```bash
python main.py --start --mode replay --pcap data/pcap_samples/test_pcap_file.pcap
```

## 📊 Résultats attendus

Lors de l'analyse du fichier PCAP, vous devriez observer:

### Alertes de Signatures
- ✅ **PORT_SCAN**: Détection de scan sur 25 ports
- ✅ **SYN_FLOOD**: Détection de 250 paquets SYN vers port 80
- ✅ **PING_SWEEP**: Détection de ping vers 20 hôtes
- ✅ **SUSPICIOUS_PORT**: Alertes pour ports 22, 3389, 445, etc.

### Alertes d'Anomalies
- ✅ **ANOMALY - High Packet Rate**: Taux de paquets >3000/min
- ✅ **ANOMALY - Large Payload**: Payload >10000 bytes
- ✅ **ANOMALY - ML**: Comportements anormaux combinés

### Statistiques attendues
- **Paquets analysés**: ~1113
- **Alertes générées**: ~10-15 alertes
- **Signatures détectées**: ~5-7
- **Anomalies détectées**: ~2-3

## 🔧 Régénérer le fichier PCAP

Pour régénérer le fichier avec des paramètres personnalisés:

```bash
# Génération par défaut
python tools/generate_test_pcap.py

# Spécifier un chemin de sortie
python tools/generate_test_pcap.py --output mon_test.pcap
```

## 📝 Notes importantes

1. **IP Source/Destination**: Tous les paquets utilisent `192.168.1.10` comme source et destination pour faciliter les tests.

2. **Timestamps**: Les paquets sont générés avec des timestamps séquentiels pour simuler un trafic réel.

3. **Payload Large**: Le payload de 50 Ko est divisé en plusieurs paquets si nécessaire (limite TCP ~65KB).

4. **Ordre des paquets**: Les paquets sont triés par timestamp avant l'écriture pour un ordre chronologique.

## 🐛 Dépannage

### Le fichier PCAP n'est pas trouvé
- Vérifiez que le fichier existe: `data/pcap_samples/test_pcap_file.pcap`
- Régénérez-le avec: `python tools/generate_test_pcap.py`

### Aucune alerte n'est générée
- Vérifiez la configuration dans `config.yaml`
- Assurez-vous que les détections sont activées:
  ```yaml
  signatures:
    portscan:
      enabled: true
    syn_flood:
      enabled: true
    ping_sweep:
      enabled: true
    suspicious_ports:
      enabled: true
  ```

### Erreur lors de la génération
- Vérifiez que Scapy est installé: `pip install scapy`
- Vérifiez les permissions d'écriture dans `data/pcap_samples/`

## 📚 Références

- [Documentation Scapy](https://scapy.readthedocs.io/)
- [Format PCAP](https://wiki.wireshark.org/Development/LibpcapFileFormat)
- [Guide IDS](README.md)

