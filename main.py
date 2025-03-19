import yt_dlp
import os
import re
import shutil
import logging

from flask import Flask, request, render_template, send_file, flash
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

app = Flask(__name__)
app.secret_key = "Z7mB4xQW2pF3vK8yL1tM9nC5dG6jR0sTQYHpVwXkJZDfNBtAqLmVgYCX2K78R5MJ"

# Dossier de téléchargement temporaire avant envoi au client
DOWNLOAD_FOLDER = "tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_filename(filename):
    """ Nettoie un nom de fichier en supprimant les caractères interdits. """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube(url, output_format):
    """ Télécharge une vidéo YouTube au format spécifié et retourne son chemin. """
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": False,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'unknown')
            clean_title = clean_filename(title)
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{clean_title}.{output_format}")
            logging.info(f"Téléchargement réussi : {file_path}")
            return file_path if os.path.exists(file_path) else None
    except Exception as e:
        error_message = f"Erreur de téléchargement : {str(e)}"
        flash(error_message, "error")
        logging.error(error_message)
        return None

def add_album_art(mp3_file: str, thumbnail_file: str):
    """ Ajoute une image comme album art dans un fichier MP3. """
    if not os.path.exists(thumbnail_file):
        logging.warning("Thumbnail non trouvé, album art ignoré.")
        return

    audio = MP3(mp3_file, ID3=ID3)
    img = Image.open(thumbnail_file).resize((500, 500))
    img.save(thumbnail_file)

    with open(thumbnail_file, "rb") as img_file:
        audio.tags.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=img_file.read()
        ))
    
    audio.save()
    logging.info(f"✅ Album art ajouté à {mp3_file}")

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Gère la page d'accueil et le formulaire de téléchargement. """
    if request.method == 'POST':
        url = request.form.get('url')
        format_choice = request.form.get('format')
        if url:
            downloaded_file = download_youtube(url, format_choice)
            if downloaded_file and os.path.exists(downloaded_file):
                if format_choice == "mp3":
                    thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
                    add_album_art(downloaded_file, thumbnail_file)
                response = send_file(downloaded_file, as_attachment=True)
                return response
            else:
                flash("Erreur : Le fichier n'a pas été généré.", "error")
                logging.error("Le fichier téléchargé est introuvable après le téléchargement.")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

# Bug to fix : Bug with https://www.youtube.com/watch?v=mE9gWUHzyzk