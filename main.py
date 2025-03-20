import yt_dlp
import os
import re

from flask import Flask, request, render_template, send_file, flash, session, redirect, url_for
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

app = Flask(__name__)
app.secret_key = "Z7mB4xQW2pF3vK8yL1tM9nC5dG6jR0sTQYHpVwXkJZDfNBtAqLmVgYCX2K78R5MJ"

DOWNLOAD_FOLDER = "tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clean_filename(filename: str) -> str:
    """ Nettoie un nom de fichier en supprimant les caractères interdits. """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube(url: str, output_format: str) -> str:
    """ Télécharge une vidéo YouTube au format spécifié et retourne son chemin. """
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
    except Exception as e:
        flash(f"Erreur de téléchargement : {str(e)}", "error")
        return None

def add_album_art(mp3_file: str, thumbnail_file: str):
    """ Ajoute une image comme album art dans un fichier MP3 si elle existe. """
    if not os.path.exists(thumbnail_file):
        return
    
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Gère la page d'accueil et le formulaire de téléchargement. """
    if request.method == 'POST':
        url = request.form.get('url')
        format_choice = request.form.get('format')
        if url:
            downloaded_file = download_youtube(url, format_choice)
            if downloaded_file and os.path.isfile(downloaded_file):
                if format_choice == "mp3":
                    add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"))
                session['download_file'] = downloaded_file
                flash("Fichier généré avec succès !", "success")
                return redirect(url_for('index'))
            else:
                flash("Erreur : Le fichier n'a pas été généré.", "error")
    return render_template('index.html', download_file=session.pop('download_file', None))

@app.route('/download')
def download():
    """ Envoie le fichier à l'utilisateur. """
    file_path = session.get('download_file')
    if file_path and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    flash("Erreur : Le fichier n'est plus disponible.", "error")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
