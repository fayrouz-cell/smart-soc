# Guide : Scanner le trafic WiFi Oreedo

## ✅ Oui, le système peut scanner votre WiFi !

Le système IDS peut capturer et analyser le trafic réseau de votre connexion WiFi Oreedo en temps réel.

## 📋 Prérequis

### 1. Installer Npcap (Windows uniquement)

Sur Windows, vous devez installer **Npcap** pour permettre la capture de paquets :

1. Téléchargez Npcap depuis : https://nmap.org/npcap/
2. Installez-le avec les options par défaut
3. **Important** : Cochez "Install Npcap in WinPcap API-compatible Mode" lors de l'installation

### 2. Privilèges administrateur

La capture en temps réel nécessite des privilèges administrateur :
- **Windows** : Clic droit sur PowerShell/Terminal > "Exécuter en tant qu'administrateur"
- **Linux/Mac** : Utilisez `sudo`

## 🔍 Étape 1 : Identifier votre interface WiFi

Exécutez le script pour lister les interfaces disponibles :

```bash
python tools/list_interfaces.py
```

Cela affichera toutes les interfaces réseau avec leurs détails. Cherchez celle qui correspond à votre WiFi (généralement nommée "Wi-Fi", "WLAN", ou similaire).

## 🚀 Étape 2 : Démarrer la capture

### Option A : Via la ligne de commande

Ouvrez un terminal **en tant qu'administrateur** et exécutez :

```bash
python main.py --start --mode live --interface "Wi-Fi"
```

Remplacez `"Wi-Fi"` par le nom exact de votre interface WiFi trouvé à l'étape 1.

### Option B : Via le fichier de configuration

Modifiez `config.yaml` :

```yaml
capture:
  mode: live  # Changer de "replay" à "live"
  interface: "Wi-Fi"  # Remplacer par votre interface WiFi
  pcap_path: data/pcap_samples/sample_traffic.pcap
  bpf_filter: ""  # Optionnel : filtrer le trafic
  throttle_packets_per_sec: 0
```

Puis exécutez :

```bash
python main.py --start
```

## 🎯 Filtres BPF (optionnel)

Vous pouvez filtrer le trafic capturé avec des filtres BPF :

```bash
# Capturer uniquement le trafic HTTP
python main.py --start --mode live --interface "Wi-Fi" --config config.yaml
# Puis dans config.yaml, ajoutez: bpf_filter: "tcp port 80"

# Capturer uniquement le trafic vers/depuis une IP spécifique
# bpf_filter: "host 192.168.1.100"

# Exclure le trafic local
# bpf_filter: "not host 192.168.1.1"
```

## 📊 Visualiser les résultats

### En temps réel

Les alertes s'affichent directement dans le terminal pendant la capture.

### Consulter les logs

```bash
# Afficher les dernières alertes
python main.py --show-alerts --tail 20

# Afficher les statistiques
python main.py --stats
```

Les logs sont également disponibles dans :
- `data/logs/traffic.log` : Tous les paquets capturés
- `data/logs/alerts.log` : Toutes les alertes générées

## ⚠️ Limitations importantes

### 1. Trafic chiffré

Le système peut voir :
- ✅ Les en-têtes des paquets (adresses IP, ports, protocoles)
- ✅ Les métadonnées (tailles, timings, patterns)
- ❌ **PAS** le contenu des données chiffrées (HTTPS, etc.)

### 2. Mode promiscuité

Sur la plupart des réseaux WiFi modernes, vous ne verrez que :
- Votre propre trafic
- Le trafic broadcast/multicast
- **PAS** le trafic des autres appareils (sauf en mode monitor, qui nécessite des cartes WiFi spéciales)

### 3. Performance

Sur des réseaux très chargés, la capture peut être intensive. Utilisez `throttle_packets_per_sec` dans la config pour limiter le débit.

## 🔧 Dépannage

### Erreur : "Permission denied"

**Solution** : Exécutez en tant qu'administrateur

### Erreur : "No network interface available"

**Solutions** :
1. Vérifiez que Npcap est installé (Windows)
2. Vérifiez que vous êtes connecté au WiFi
3. Listez les interfaces : `python tools/list_interfaces.py`

### Erreur : "Interface not found"

**Solution** : Utilisez le nom exact de l'interface (sensible à la casse). Sur Windows, utilisez des guillemets si le nom contient des espaces :
```bash
--interface "Wi-Fi"
```

### Aucun paquet capturé

**Vérifications** :
1. Êtes-vous connecté au WiFi ?
2. Y a-t-il du trafic réseau actif ?
3. Testez avec un filtre large : `bpf_filter: "tcp or udp"`

## 📝 Exemple complet

```bash
# 1. Lister les interfaces
python tools/list_interfaces.py

# 2. Démarrer la capture (en tant qu'admin)
python main.py --start --mode live --interface "Wi-Fi"

# 3. Dans un autre terminal, générer du trafic (ouvrir un site web, etc.)

# 4. Arrêter avec Ctrl+C

# 5. Consulter les alertes
python main.py --show-alerts --tail 10
```

## 🔒 Sécurité et légalité

⚠️ **IMPORTANT** :
- Utilisez uniquement sur votre propre réseau ou avec autorisation
- Respectez les lois locales sur l'interception de trafic réseau
- Ne capturez pas de trafic sur des réseaux publics sans autorisation explicite
- Les données capturées peuvent contenir des informations sensibles

## 💡 Astuces

1. **Mode replay pour tester** : Testez d'abord avec `--mode replay` pour vous familiariser
2. **Filtres spécifiques** : Utilisez des filtres BPF pour réduire le volume de données
3. **Logs rotatifs** : Les logs sont automatiquement rotatifs (10MB max, 7 backups)
4. **Interface web** : Utilisez `python web/run_web.py` pour une interface graphique

## 🆘 Besoin d'aide ?

Consultez :
- `README.md` : Documentation complète
- `python main.py --help` : Aide en ligne
- `python tools/list_interfaces.py` : Liste des interfaces

