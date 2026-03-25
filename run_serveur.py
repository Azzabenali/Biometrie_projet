# run_server.py — à lancer depuis Biometrie_projet/
import sys
import os

# Ajouter le dossier zero_knowledge_auth au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "zero_knowledge_auth"))

from serveur.api import app
from serveur.database import init_db

if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5000,       # HTTP pour l'instant, HTTPS en S4
        debug=True
    )