# ✅ Mise à Jour du Seuil de Taux de Paquets à 3000 packets/min

## 🎯 Modification

Le seuil de détection d'anomalie pour le taux de paquets a été augmenté de **1000** à **3000 packets/min**.

## 📊 Comportement

### Trafic Normal
- **≤ 3000 packets/min** : Trafic considéré comme normal
- Affichage en **cyan** (couleur normale)
- Aucune alerte générée

### Trafic Élevé (Warning)
- **> 3000 packets/min** : Trafic considéré comme élevé
- Affichage en **jaune/orange** (warning)
- Alerte `ANOMALY_HIGH_RATE` générée avec sévérité **WARNING**

### Trafic Critique
- **> 6000 packets/min** (2x le seuil) : Trafic considéré comme critique
- Affichage en **rouge** (danger)
- Alerte `ANOMALY_HIGH_RATE` générée avec sévérité **WARNING**

## 📝 Fichiers Modifiés

### 1. `config.yaml`
```yaml
anomaly:
  packet_rate_threshold: 3000  # per src per minute (augmenté de 1000)
```

### 2. `web/static/js/dashboard.js`
- Seuil mis à jour dans `updatePacketRateDisplay()` : **3000 packets/min**
- Zones de couleur ajustées :
  - Normal : ≤ 3000 packets/min (cyan)
  - Warning : > 3000 packets/min (jaune)
  - Critical : > 6000 packets/min (rouge)

### 3. `core/anomaly_engine.py`
- Utilise automatiquement le nouveau seuil depuis `config.yaml`
- Génère des alertes `ANOMALY_HIGH_RATE` quand le taux dépasse 3000 packets/min

## 🔔 Alertes Générées

Quand le taux dépasse **3000 packets/min**, une alerte est générée :

```
Rule: ANOMALY_HIGH_RATE
Severity: WARNING
Description: Unusually high packet rate: [rate] packets/min
Metadata: {
  "packet_rate": [rate],
  "threshold": 3000
}
```

## 🎨 Affichage Visuel

### Carte "Taux de Paquets"
- **Cyan** : ≤ 3000 packets/min (normal)
- **Jaune** : > 3000 packets/min (warning)
- **Rouge** : > 6000 packets/min (critical)

### Graphique
- Affiche le taux réel en packets/min
- Historique des 30 dernières secondes
- Mise à jour toutes les secondes

## ✅ Résultat

- ✅ Seuil augmenté à 3000 packets/min
- ✅ Alertes générées au-delà de 3000 packets/min
- ✅ Affichage visuel mis à jour (couleurs)
- ✅ Compatible avec le système de détection existant

---

**Status**: ✅ Seuil mis à jour et fonctionnel

