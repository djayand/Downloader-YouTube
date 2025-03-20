import yt_dlp
import os
import re

from flask import Flask, request, render_template, send_file, flash
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

app = Flask(__name__)
app.secret_key = "Z7mB4xQW2pF3vK8yL1tM9nC5dG6jR0sTQYHpVwXkJZDfNBtAqLmVgYCX2K78R5MJ"

# Dossier de téléchargement temporaire avant envoi au client
DOWNLOAD_FOLDER = "tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Nettoie un nom de fichier en supprimant les caractères interdits.
def clean_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Télécharge une vidéo YouTube au format spécifié et retourne son chemin.
def download_youtube(url: str, output_format: str) -> str:
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,  # Réduit les logs pour améliorer la performance
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
            title = info_dict.get('title', 'unknown')
            clean_title = clean_filename(title)
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{clean_title}.mp3" if output_format == "mp3" else f"{clean_title}.mp4")
            return file_path if os.path.isfile(file_path) else None
    except Exception as e:
        flash(f"Erreur de téléchargement : {str(e)}", "error")
        return None

# Ajoute une image comme album art dans un fichier MP3 si elle existe.
def add_album_art(mp3_file: str, thumbnail_file: str):
    if not os.path.exists(thumbnail_file):
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Gère la page d'accueil et le formulaire de téléchargement."""
    if request.method == 'POST':
        url = request.form.get('url')
        format_choice = request.form.get('format')
        if url:
            downloaded_file = download_youtube(url, format_choice)
            if downloaded_file and os.path.isfile(downloaded_file):
                if format_choice == "mp3":
                    thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
                    add_album_art(downloaded_file, thumbnail_file)
                return send_file(downloaded_file, as_attachment=True)
            else:
                flash("Erreur : Le fichier n'a pas été généré.", "error")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
