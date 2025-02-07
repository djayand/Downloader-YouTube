import os
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

def download_youtube(url: str, output_format: str = "mp4"):
    """
    Télécharge une vidéo YouTube en MP4 ou l'audio en MP3 avec l'album art.
    
    :param url: URL de la vidéo YouTube
    :param output_format: "mp4" pour la vidéo, "mp3" pour l'audio
    :return: Chemin du fichier téléchargé
    """
    output_template = "%(title)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": False
    }
    
    if output_format == "mp4":
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        })
    elif output_format == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                },
                {
                    "key": "EmbedThumbnail"
                }
            ],
            "writethumbnail": True,
            "postprocessor_args": [
                "-id3v2_version", "3"
            ]
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'unknown')
        return f"{title}.{output_format}"

def add_album_art(mp3_file: str, thumbnail_file: str):
    """
    Ajoute une miniature en tant qu'album art à un fichier MP3.
    
    :param mp3_file: Chemin du fichier MP3
    :param thumbnail_file: Chemin de la miniature
    """
    if not os.path.exists(thumbnail_file):
        print("Thumbnail not found, skipping album art embedding.")
        return

    audio = MP3(mp3_file, ID3=ID3)
    
    # Vérifier si la miniature est au bon format
    img = Image.open(thumbnail_file)
    img = img.resize((500, 500))  # Redimensionnement à 500x500 pour être carré
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
    print(f"Album art ajouté à {mp3_file}")

if __name__ == "__main__":
    url = input("Entrez l'URL de la vidéo YouTube : ")
    format_choice = input("Format (mp4/mp3) ? ").strip().lower()
    
    if format_choice not in ["mp4", "mp3"]:
        print("Format invalide, choisissez 'mp4' ou 'mp3'.")
    else:
        downloaded_file = download_youtube(url, format_choice)
        
        if format_choice == "mp3":
            thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
            add_album_art(downloaded_file, thumbnail_file)
        
        print(f"Fichier téléchargé : {downloaded_file}")
