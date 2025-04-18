import os
import re
import shutil
import subprocess
import yt_dlp

from flask import Flask, request, render_template, send_file, flash, session, redirect, url_for, jsonify
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from uuid import uuid4

# Chargement automatique des variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv()

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Dossier temporaire de téléchargement
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "tmp")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Dictionnaire pour suivre l’état de chaque tâche (via AJAX)
tasks_status = {}

# === UTILS ===

def is_valid_url(url: str) -> bool:
    """Vérifie si l'URL fournie semble être une URL YouTube valide."""
    yt_regex = re.compile(r"^(https?\:\/\/)?(www\\.youtube\\.com|youtu\\.?be)\\/.+$")
    return bool(yt_regex.match(url))

def is_ffmpeg_installed() -> bool:
    """Vérifie si FFmpeg est installé et accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def clean_filename(filename: str) -> str:
    """Nettoie un nom de fichier en supprimant les caractères interdits pour le système de fichiers."""
    return re.sub(r'[<>:"/\\\\|?*]', '_', filename)

# === TÉLÉCHARGEMENT ===

def download_youtube(url: str, output_format: str) -> str:
    """
    Télécharge une vidéo YouTube dans le format demandé (mp3 ou mp4).
    Retourne le chemin du fichier généré.
    """
    if not is_ffmpeg_installed():
        return None

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "quiet": True,
        "format": "bestaudio/best" if output_format == "mp3" else "bestvideo+bestaudio",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }] if output_format == "mp3" else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = clean_filename(info_dict.get('title', 'unknown'))
            return os.path.join(DOWNLOAD_FOLDER, f"{title}.{'mp3' if output_format == 'mp3' else 'mp4'}")
    except Exception:
        return None

def add_album_art(mp3_file: str, thumbnail_file: str):
    """
    Ajoute une miniature au fichier MP3 (image en couverture).
    Ignore si l'image n’est pas présente.
    """
    if not os.path.exists(mp3_file) or not os.path.exists(thumbnail_file):
        return
    try:
        audio = MP3(mp3_file, ID3=ID3)
        with open(thumbnail_file, "rb") as img_file:
            audio.tags.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=img_file.read()
            ))
        audio.save()
    except Exception:
        pass

# === ROUTES ===

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Page d'accueil : formulaire + gestion POST pour le téléchargement.
    Retourne un task_id au frontend pour le suivi du statut.
    """
    if request.method == 'POST':
        task_id = str(uuid4())
        tasks_status[task_id] = {'status': 'processing', 'message': 'Téléchargement en cours...'}

        url = request.form.get('url')
        format_choice = request.form.get('format')

        if not url or not is_valid_url(url):
            tasks_status[task_id] = {'status': 'error', 'message': "URL YouTube invalide."}
            return jsonify({'task_id': task_id})

        downloaded_file = download_youtube(url, format_choice)
        if downloaded_file and os.path.isfile(downloaded_file):
            if format_choice == "mp3":
                add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"))

            session['download_file'] = downloaded_file
            tasks_status[task_id] = {'status': 'success', 'message': "Fichier généré avec succès !"}
        else:
            tasks_status[task_id] = {'status': 'error', 'message': "Le fichier n'a pas pu être généré."}

        return jsonify({'task_id': task_id})

    return render_template('index.html', download_file=session.get('download_file'))

@app.route('/status/<task_id>')
def task_status(task_id):
    """
    Route de suivi de tâche (appelée par le frontend via AJAX).
    Retourne l'état en temps réel.
    """
    status = tasks_status.get(task_id, {'status': 'unknown', 'message': 'Tâche introuvable'})
    return jsonify(status)

@app.route('/download')
def download():
    """
    Route qui fournit le fichier généré à l'utilisateur.
    Supprime la référence du fichier de la session après envoi.
    """
    file_path = session.get('download_file')
    if file_path and os.path.isfile(file_path):
        session.pop('download_file', None)
        return send_file(file_path, as_attachment=True)

    flash("Erreur : Le fichier n'est plus disponible.", "error")
    return redirect(url_for('index'))

@app.route('/clear')
def clear():
    """
    Supprime tous les fichiers temporaires pour libérer l’espace disque.
    """
    try:
        shutil.rmtree(DOWNLOAD_FOLDER)
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        session.pop('download_file', None)
        flash("Tous les fichiers temporaires ont été supprimés.", "success")
    except Exception as e:
        flash(f"Erreur lors du nettoyage : {str(e)}", "error")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)