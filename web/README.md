# Interface Web IDS

Interface web Flask pour le Système de Détection d'Intrusions Réseau (IDS).

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancer l'interface web

**Windows:**
```bash
scripts\run_web.bat
```

**Linux/Mac:**
```bash
python web/run_web.py
```

L'interface sera accessible sur: **http://localhost:5000**

## 👤 Comptes de démonstration

- **Administrateur**: `admin` / `admin123`
- **Utilisateur**: `user` / `user123`

## 📋 Fonctionnalités

### Page d'accueil
- Présentation du système IDS
- Vue d'ensemble des fonctionnalités
- Liens vers les différentes sections

### Tableau de bord (Dashboard)
- **Surveillance en temps réel** via WebSocket
- Affichage des paquets analysés en direct
- Alertes en temps réel avec codes couleur
- Statistiques (paquets, alertes, temps d'activité)
- Graphiques interactifs (Chart.js)
- Contrôle IDS (démarrer/arrêter) - Admin uniquement

### Historique des détections
- Liste complète des alertes passées
- Filtres avancés :
  - Type d'attaque
  - Gravité (CRITICAL, WARNING, INFO)
  - Plage de dates
- Recherche et tri
- Détails complets de chaque alerte

### Configuration des alertes
- **Détection par signatures** :
  - Port scan (seuil et fenêtre temporelle)
  - SYN flood
  - Ping sweep
  - Ports suspects
- **Détection d'anomalies** :
  - Seuil de taux de paquets
  - Seuil de taille de payload
  - Activation Machine Learning
- **Accès restreint** : Admin uniquement

### Page de contact
- Formulaire de contact
- Support et informations

## 🔐 Sécurité

- Authentification par session
- Rôles utilisateur (admin/user)
- Protection des routes sensibles
- Sessions sécurisées avec Flask

## 🛠️ Technologies utilisées

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: Bootstrap 5, Chart.js
- **WebSocket**: Socket.IO pour le temps réel
- **Authentification**: Werkzeug (hash de mots de passe)

## 📝 Notes importantes

1. **Mode Live**: Nécessite des privilèges administrateur
2. **Mode Replay**: Recommandé pour les tests (utilise des fichiers PCAP)
3. **Configuration**: Les modifications de configuration ne sont pas persistées dans cette version (à améliorer en production)
4. **Base de données**: Les utilisateurs sont stockés en mémoire (à remplacer par une vraie base de données en production)

## 🔧 Développement

### Structure des fichiers

```
web/
├── app.py              # Application Flask principale
├── run_web.py          # Script de démarrage
├── __init__.py
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── history.html
│   ├── alerts.html
│   └── contact.html
└── static/             # Fichiers statiques
    ├── css/
    │   └── style.css
    └── js/
        ├── dashboard.js
        ├── history.js
        ├── alerts.js
        └── contact.js
```

### API Endpoints

- `GET /api/stats` - Statistiques actuelles
- `GET /api/alerts` - Liste des alertes (avec filtres)
- `GET /api/config` - Configuration actuelle
- `POST /api/config` - Mettre à jour la configuration (Admin)
- `POST /api/ids/start` - Démarrer l'IDS (Admin)
- `POST /api/ids/stop` - Arrêter l'IDS (Admin)
- `GET /api/ids/status` - Statut de l'IDS

### WebSocket Events

- `connect` - Connexion client
- `new_alert` - Nouvelle alerte détectée
- `new_packet` - Nouveau paquet analysé

## 🐛 Dépannage

### Erreur de port déjà utilisé
```bash
# Changer le port dans web/run_web.py
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Module Flask manquant
```bash
pip install flask flask-socketio werkzeug
```

### WebSocket ne fonctionne pas
- Vérifier que Flask-SocketIO est installé
- Vérifier la console du navigateur pour les erreurs
- S'assurer que Socket.IO client est chargé dans les templates

## 📚 Améliorations futures

- [ ] Persistance de la configuration dans config.yaml
- [ ] Base de données pour les utilisateurs
- [ ] Export des alertes (CSV, PDF)
- [ ] Notifications par email
- [ ] Dashboard avec plus de métriques
- [ ] Historique des paquets
- [ ] Filtres BPF personnalisés
- [ ] Mode dark/light













