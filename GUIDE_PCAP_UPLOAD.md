# 📁 Guide : Import et Exemples de Fichiers PCAP

## ✅ Nouvelles Fonctionnalités

### 1. 📤 Import de Fichiers PCAP

Vous pouvez maintenant **importer vos propres fichiers PCAP** depuis votre ordinateur directement via l'interface web !

**Fonctionnalités** :
- ✅ Upload de fichiers `.pcap`, `.pcapng`, `.cap`
- ✅ Taille maximale : 500MB
- ✅ Sécurité : validation du type de fichier
- ✅ Protection contre l'écrasement (ajout de timestamp si fichier existe)
- ✅ Feedback visuel pendant l'upload
- ✅ Actualisation automatique de la liste après upload

**Comment utiliser** :
1. Allez au **Dashboard**
2. Dans la section "Fichier PCAP", trouvez la section **"Importer un fichier PCAP"**
3. Cliquez sur **"Parcourir"** et sélectionnez votre fichier
4. Cliquez sur **"Upload"**
5. Le fichier sera automatiquement ajouté à la liste disponible

### 2. 🎯 Fichiers d'Exemple pour Tests

7 fichiers PCAP d'exemple ont été générés pour vous permettre de tester le système :

#### 📋 Liste des Fichiers d'Exemple

1. **`trafic_benin.pcap`** (150 paquets)
   - Trafic réseau normal
   - Ports communs (80, 443, 53, 22, etc.)
   - Mix TCP, UDP, ICMP
   - **Usage** : Tester le comportement normal

2. **`port_scan.pcap`** (30 paquets)
   - Scan de ports depuis 192.168.1.100 vers 192.168.1.5
   - 30 ports différents scannés rapidement
   - **Usage** : Tester la détection de port scan

3. **`syn_flood.pcap`** (250 paquets)
   - Attaque SYN flood depuis 192.168.1.101 vers 192.168.1.5:80
   - 250 paquets SYN en très peu de temps
   - **Usage** : Tester la détection de SYN flood

4. **`ping_sweep.pcap`** (60 paquets)
   - Ping sweep sur le réseau 192.168.1.0/24
   - 60 hôtes différents pingés
   - **Usage** : Tester la détection de ping sweep

5. **`ports_suspects.pcap`** (7 paquets)
   - Tentatives d'accès à des ports suspects
   - Ports : 21, 22, 23, 3389, 4444, 6667, 31337
   - **Usage** : Tester la détection de ports suspects

6. **`attaque_mixte.pcap`** (282 paquets)
   - Combinaison de plusieurs attaques :
     - Port scan
     - SYN flood
     - Ping sweep
     - Accès ports suspects
   - **Usage** : Tester la détection de multiples attaques

7. **`trafic_mixte.pcap`** (325 paquets)
   - Mix de trafic bénin et attaques
   - Trafic normal + port scan + SYN flood
   - **Usage** : Tester la détection dans un trafic réaliste

### 3. 🔧 Génération de Fichiers d'Exemple

**Via l'interface web** (Admin uniquement) :
1. Allez au Dashboard
2. Cliquez sur le bouton **"Générer exemples"** dans la section PCAP
3. Attendez quelques secondes
4. Les fichiers seront générés dans `data/pcap_samples/`

**Via la ligne de commande** :
```bash
python tools/generate_examples.py
```

**Options disponibles** :
```bash
python tools/generate_examples.py --output-dir "data/pcap_samples"
```

## 🚀 Utilisation

### Scénario 1 : Tester avec un Fichier d'Exemple

1. **Connectez-vous** à l'interface web (admin/admin123)
2. Allez au **Dashboard**
3. Sélectionnez **"Replay (PCAP)"** comme mode
4. Dans le sélecteur de dossier, choisissez **"data/pcap_samples"**
5. Dans la liste des fichiers, sélectionnez un fichier d'exemple (ex: `port_scan.pcap`)
6. Cliquez sur **"Démarrer IDS"**
7. Observez les alertes générées !

### Scénario 2 : Importer et Analyser Votre Fichier

1. **Préparez votre fichier PCAP** sur votre ordinateur
2. Allez au **Dashboard**
3. Sélectionnez **"Replay (PCAP)"** comme mode
4. Dans la section **"Importer un fichier PCAP"** :
   - Cliquez sur **"Parcourir"**
   - Sélectionnez votre fichier `.pcap`, `.pcapng` ou `.cap`
   - Cliquez sur **"Upload"**
5. Attendez la confirmation d'upload
6. Votre fichier apparaîtra dans la liste
7. Sélectionnez-le et cliquez sur **"Démarrer IDS"**

### Scénario 3 : Générer de Nouveaux Exemples

1. Allez au **Dashboard** (en tant qu'admin)
2. Cliquez sur **"Générer exemples"**
3. Attendez la confirmation
4. Les nouveaux fichiers seront disponibles dans la liste

## 📊 Détails Techniques

### Formats Supportés

- ✅ `.pcap` - Format PCAP standard
- ✅ `.pcapng` - Format PCAP Next Generation
- ✅ `.cap` - Format CAP (ancien format)

### Limitations

- **Taille maximale** : 500MB par fichier
- **Dossier d'upload** : `data/pcap_samples/` (par défaut)
- **Permissions** : Upload disponible pour tous les utilisateurs connectés
- **Génération** : Disponible uniquement pour les administrateurs

### Sécurité

- ✅ Validation du type de fichier (extension)
- ✅ Noms de fichiers sécurisés (sanitization)
- ✅ Protection contre l'écrasement (timestamp ajouté si conflit)
- ✅ Limite de taille pour éviter les abus
- ✅ Authentification requise pour l'upload

## 🎯 Exemples de Tests Recommandés

### Test 1 : Détection de Port Scan
- **Fichier** : `port_scan.pcap`
- **Résultat attendu** : Alerte "PORT_SCAN" avec ~30 ports détectés

### Test 2 : Détection de SYN Flood
- **Fichier** : `syn_flood.pcap`
- **Résultat attendu** : Alerte "SYN_FLOOD" CRITICAL avec ~250 SYN packets

### Test 3 : Détection de Ping Sweep
- **Fichier** : `ping_sweep.pcap`
- **Résultat attendu** : Alerte "PING_SWEEP" avec ~60 hôtes détectés

### Test 4 : Détection Multi-Attaques
- **Fichier** : `attaque_mixte.pcap`
- **Résultat attendu** : Plusieurs alertes de différents types

### Test 5 : Trafic Normal
- **Fichier** : `trafic_benin.pcap`
- **Résultat attendu** : Peu ou pas d'alertes (trafic normal)

## 🔧 Dépannage

### L'upload échoue
- Vérifiez que le fichier fait moins de 500MB
- Vérifiez que l'extension est `.pcap`, `.pcapng` ou `.cap`
- Vérifiez les permissions du dossier `data/pcap_samples/`

### Les fichiers d'exemple ne s'affichent pas
- Cliquez sur le bouton "Actualiser" (icône de rafraîchissement)
- Vérifiez que le dossier `data/pcap_samples/` existe
- Vérifiez les permissions de lecture

### La génération échoue
- Vérifiez que Scapy est installé : `pip install scapy`
- Vérifiez que vous êtes connecté en tant qu'admin
- Vérifiez les logs dans la console du serveur

## 📝 Notes

- Les fichiers uploadés sont stockés dans `data/pcap_samples/`
- Les fichiers générés peuvent être supprimés manuellement si nécessaire
- Les fichiers d'exemple peuvent être régénérés à tout moment
- Les fichiers uploadés conservent leur nom original (avec timestamp si conflit)

---

**Version** : 2.1.0  
**Date** : 2025

