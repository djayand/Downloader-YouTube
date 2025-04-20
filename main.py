import os
import logging

from flask import Flask
from dotenv import load_dotenv

# Suppression des logs FLASK
log = logging.getLogger('werkzeug')
log.disabled = True

# Chargement des variables d'environnement
load_dotenv()

# Initialisation de Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configuration dossier de téléchargement
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "tmp")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Import des routes (elles reçoivent l'app Flask)
from routes import register_routes
register_routes(app, DOWNLOAD_FOLDER)

if __name__ == "__main__":
    app.run(debug=True)