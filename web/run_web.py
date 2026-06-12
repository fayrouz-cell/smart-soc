#!/usr/bin/env python3
"""Script to run the Flask web interface."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app, socketio

if __name__ == '__main__':
    print("=" * 60)
    print("Démarrage de l'interface web IDS")
    print("=" * 60)
    print("\nAccédez à l'interface sur: http://localhost:5000")
    print("\nComptes de démonstration:")
    print("  Admin: admin / admin123")
    print("  Utilisateur: user / user123")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60)
    print()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)













