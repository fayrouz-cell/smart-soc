# **► Network Intrusion Detection System (IDS)**

**Développé par : Fayrouz Jbeli**

Network Intrusion Detection System (IDS)  
Un système complet de détection d'intrusion réseau écrit en Python, capable de détecter des attaques basées sur des signatures et des anomalies statistiques.

---

## **► Table des matières**

- Vue d'ensemble
- Architecture
- Installation
- Utilisation
- Configuration
- Tests
- Docker
- Sécurité
- Dépannage

---

## **► Vue d'ensemble**

Ce projet implémente un IDS (Intrusion Detection System) avec les fonctionnalités suivantes :

- Capture de paquets : Mode live (capture en temps réel) et replay (lecture de fichiers PCAP)
- Détection par signatures : Port scan, SYN flood, ping sweep, ports suspects
- Détection d'anomalies : Statistiques et optionnellement Machine Learning (IsolationForest)
- Journalisation structurée : Logs JSON avec rotation automatique
- Alertes en temps réel : Affichage coloré avec Rich/Colorama
- Tests complets : Suite de tests pytest

---

## **► Architecture**

![Architecture](architecture.png)  
*Remplace `architecture.png` par le chemin de ton image (ex: `docs/architecture.png`)*

Modules principaux :

- `core/sniffer.py` : Capture de paquets réseau
- `core/packet_parser.py` : Parsing et normalisation des paquets
- `core/signature_engine.py` : Détection basée sur des règles de signatures
- `core/anomaly_engine.py` : Détection d'anomalies statistiques et ML
- `core/logger.py` : Journalisation structurée JSON
- `core/alert.py` : Gestion et affichage des alertes
- `cli/interface.py` : Interface en ligne de commande
- `main.py` : Point d'entrée principal

---

## **► Installation**

### Prérequis

- Python 3.10+
- pip
- Sur Linux : privilèges root pour la capture live (ou utiliser le mode replay)

### Installation avec pip

```bash
# Cloner ou télécharger le projet
cd IDS_Project

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
