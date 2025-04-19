import os
import re
import subprocess
import yt_dlp

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def is_valid_url(url: str) -> bool:
    """Vérifie si l'URL semble être une URL YouTube valide (classique ou short)."""
    yt_regex = re.compile(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$')
    return bool(yt_regex.match(url))

def is_ffmpeg_installed() -> bool:
    """Vérifie si FFmpeg est installé et accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def clean_filename(filename: str) -> str:
    """Nettoie un nom de fichier en supprimant les caractères interdits."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube(url: str, output_format: str, download_folder: str, status_callback=None) -> str:
    """
    Télécharge une vidéo YouTube dans le format demandé (mp3 ou mp4).
    Retourne le chemin du fichier généré.
    Met à jour le statut via le callback à chaque étape.
    """
    if not is_ffmpeg_installed():
        if status_callback:
            status_callback("error", "❌ FFmpeg n'est pas installé.")
        return None

    if status_callback:
        status_callback("processing", "🔍 Vérification de l'URL...")

    ydl_opts = {
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
        "quiet": True,
        "format": "bestaudio/best" if output_format == "mp3" else "bestvideo+bestaudio",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }] if output_format == "mp3" else []
    }

    try:
        if status_callback:
            status_callback("processing", "🎬 Extraction des métadonnées YouTube...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)

        if status_callback:
            status_callback("processing", "⬇️ Téléchargement terminé, traitement du fichier...")

        title = clean_filename(info_dict.get('title', 'unknown'))
        final_file = os.path.join(download_folder, f"{title}.{'mp3' if output_format == 'mp3' else 'mp4'}")

        return final_file
    except Exception as e:
        if status_callback:
            status_callback("error", f"❌ Erreur : {str(e)}")
        return None

def add_album_art(mp3_file: str, thumbnail_file: str, status_callback=None):
    """
    Ajoute une miniature au fichier MP3 si elle est disponible.
    Met à jour le statut via le callback.
    """
    if not os.path.exists(mp3_file):
        if status_callback:
            status_callback("error", "❌ Le fichier MP3 est introuvable.")
        return

    if not os.path.exists(thumbnail_file):
        if status_callback:
            status_callback("processing", "ℹ️ Aucune miniature trouvée, mais le MP3 est prêt.")
        return

    try:
        if status_callback:
            status_callback("processing", "🖼 Ajout de la miniature dans le fichier MP3...")

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
        if status_callback:
            status_callback("error", "❌ Erreur lors de l'ajout de la miniature.")