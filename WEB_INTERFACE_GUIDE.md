# Guide d'utilisation de l'interface web IDS

## 🎉 Interface web créée avec succès !

Une interface web complète a été ajoutée à votre projet IDS. Voici comment l'utiliser.

## 📦 Installation

### 1. Installer les nouvelles dépendances

```bash
# Activer l'environnement virtuel si nécessaire
venv\Scripts\activate

# Installer les dépendances Flask
pip install -r requirements.txt
```

Les nouvelles dépendances incluent :
- `flask>=2.3.0` - Framework web
- `flask-socketio>=5.3.0` - WebSocket pour le temps réel
- `werkzeug>=2.3.0` - Utilitaires Flask (sécurité, sessions)

## 🚀 Démarrage

### Option 1 : Script Windows (recommandé)
```bash
scripts\run_web.bat
```

### Option 2 : Commande Python
```bash
python web\run_web.py
```

L'interface sera accessible sur : **http://localhost:5000**

## 👤 Connexion

Deux comptes sont disponibles par défaut :

| Rôle | Nom d'utilisateur | Mot de passe |
|------|-------------------|-------------|
| **Administrateur** | `admin` | `admin123` |
| **Utilisateur** | `user` | `user123` |

**Note** : Seuls les administrateurs peuvent démarrer/arrêter l'IDS et modifier la configuration.

## 📱 Pages disponibles

### 1. Page d'accueil (`/`)
- Présentation du système
- Vue d'ensemble des fonctionnalités
- Liens vers toutes les sections

### 2. Tableau de bord (`/dashboard`)
**Fonctionnalités principales :**
- ✅ Surveillance en temps réel via WebSocket
- ✅ Affichage des paquets analysés en direct
- ✅ Alertes en temps réel avec codes couleur
- ✅ Statistiques (paquets, alertes, temps d'activité)
- ✅ Graphiques interactifs (alertes par type, taux de paquets)
- ✅ Contrôle IDS (démarrer/arrêter) - **Admin uniquement**

**Comment utiliser :**
1. Connectez-vous en tant qu'admin
2. Dans le panneau "Contrôle IDS", choisissez le mode :
   - **Replay** : Analyse un fichier PCAP (recommandé pour débuter)
   - **Live** : Capture en temps réel (nécessite privilèges admin)
3. Cliquez sur "Démarrer IDS"
4. Observez le trafic et les alertes en temps réel !

### 3. Historique (`/history`)
- Liste complète des alertes passées
- **Filtres avancés** :
  - Type d'attaque (Port Scan, SYN Flood, etc.)
  - Gravité (CRITICAL, WARNING, INFO)
  - Plage de dates
- Détails complets de chaque alerte (clic sur une ligne)

### 4. Configuration des alertes (`/alerts`)
**Admin uniquement** - Permet de configurer :
- **Détection par signatures** :
  - Port scan (seuil et fenêtre temporelle)
  - SYN flood
  - Ping sweep
  - Ports suspects
- **Détection d'anomalies** :
  - Seuil de taux de paquets
  - Seuil de taille de payload
  - Activation Machine Learning

### 5. Contact (`/contact`)
- Formulaire de contact
- Informations de support

## 🔄 Flux de travail recommandé

1. **Démarrer l'interface web**
   ```bash
   python web\run_web.py
   ```

2. **Se connecter** avec le compte admin

3. **Aller au tableau de bord** et démarrer l'IDS en mode replay :
   - Mode : Replay
   - Chemin PCAP : `data\pcap_samples\sample_traffic.pcap`
   - Cliquer sur "Démarrer IDS"

4. **Observer** les paquets et alertes en temps réel

5. **Consulter l'historique** pour voir toutes les alertes passées

6. **Configurer les seuils** dans la page Alertes si nécessaire

## 🎨 Fonctionnalités visuelles

- **Interface responsive** : Fonctionne sur desktop, tablette et mobile
- **Codes couleur** :
  - 🔴 Rouge : Alertes CRITICAL
  - 🟡 Jaune : Alertes WARNING
  - 🔵 Bleu : Alertes INFO
- **Graphiques interactifs** : Chart.js pour visualiser les données
- **Temps réel** : WebSocket pour les mises à jour instantanées

## 🔐 Sécurité

- ✅ Authentification par session
- ✅ Rôles utilisateur (admin/user)
- ✅ Protection des routes sensibles
- ✅ Hash des mots de passe (Werkzeug)

**⚠️ Note de sécurité** : En production, changez le `SECRET_KEY` dans `web/app.py` et utilisez une vraie base de données pour les utilisateurs.

## 🐛 Dépannage

### L'interface ne démarre pas
```bash
# Vérifier que Flask est installé
pip install flask flask-socketio werkzeug

# Vérifier qu'il n'y a pas d'erreur de port
# Si le port 5000 est occupé, modifiez le port dans web/run_web.py
```

### WebSocket ne fonctionne pas
- Vérifiez la console du navigateur (F12) pour les erreurs
- Assurez-vous que Socket.IO est chargé (vérifiez dans base.html)

### L'IDS ne démarre pas depuis l'interface
- Vérifiez que vous êtes connecté en tant qu'admin
- Vérifiez que le fichier PCAP existe (mode replay)
- Vérifiez les logs dans la console Python

### Les alertes n'apparaissent pas
- Vérifiez que l'IDS est bien démarré
- Vérifiez les logs dans `data\logs\alerts.log`
- Vérifiez la connexion WebSocket dans la console du navigateur

## 📁 Structure créée

```
IDS_Project/
├── web/
│   ├── app.py              # Application Flask principale
│   ├── run_web.py           # Script de démarrage
│   ├── __init__.py
│   ├── templates/           # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── history.html
│   │   ├── alerts.html
│   │   └── contact.html
│   ├── static/              # Fichiers statiques
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── dashboard.js
│   │       ├── history.js
│   │       ├── alerts.js
│   │       └── contact.js
│   └── README.md
├── scripts/
│   └── run_web.bat          # Script de démarrage Windows
└── requirements.txt          # Mis à jour avec Flask
```

## 🚀 Prochaines étapes

1. **Tester l'interface** : Lancez `python web\run_web.py` et explorez toutes les pages
2. **Générer un PCAP** : Si vous n'avez pas de fichier PCAP, utilisez :
   ```bash
   python tools\pcap_generator.py --output data\pcap_samples\sample_traffic.pcap
   ```
3. **Personnaliser** : Modifiez les templates et styles selon vos besoins
4. **Sécuriser** : En production, changez les mots de passe et utilisez une vraie base de données

## 💡 Astuces

- **Mode replay recommandé** : Pour tester sans privilèges admin
- **Ouvrir dans plusieurs onglets** : Vous pouvez avoir le dashboard et l'historique ouverts en même temps
- **Console du navigateur** : Utilisez F12 pour voir les logs WebSocket et déboguer
- **Graphiques** : Les graphiques se mettent à jour automatiquement en temps réel

## 📞 Support

Pour toute question ou problème, consultez :
- `web/README.md` - Documentation détaillée
- Les logs dans `data\logs\`
- La console du navigateur (F12) pour les erreurs JavaScript

---

**Bon monitoring ! 🛡️**













