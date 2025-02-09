import os
import yt_dlp

import curses  # Pour la navigation interactive sur Linux/macOS
import keyboard  # Alternative pour Windows

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

def download_youtube(url: str, output_format: str):
    """
    Télécharge une vidéo YouTube en MP4 ou en extrait l'audio en MP3.

    :param url: URL de la vidéo YouTube
    :param output_format: "mp4" pour la vidéo, "mp3" pour l'audio
    :return: Chemin du fichier téléchargé
    """
    output_template = "%(title)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_template,  # Définir le nom de sortie du fichier
        "quiet": False  # Affiche les logs de yt-dlp
    }
    
    if output_format == "mp4":
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",  # Télécharge la meilleure qualité vidéo + audio
            "merge_output_format": "mp4"  # Fusionne les deux en MP4
        })
    elif output_format == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",  # Télécharge uniquement l'audio
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                },
                {
                    "key": "EmbedThumbnail"  # Ajoute la miniature comme album art
                }
            ],
            "writethumbnail": True,
            "postprocessor_args": ["-id3v2_version", "3"]
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
        print("Thumbnail non trouvée, album art ignoré.")
        return

    audio = MP3(mp3_file, ID3=ID3)

    # Assurer que la miniature est carrée et de bonne taille
    img = Image.open(thumbnail_file)
    img = img.resize((500, 500))  # Redimensionner à 500x500 pixels
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
    print(f"✅ Album art ajouté à {mp3_file}")

def menu():
    """
    Affiche un menu interactif permettant de choisir entre :
    - Télécharger en MP3
    - Télécharger en MP4
    - Quitter l'application
    """
    options = ["Télécharger MP3", "Télécharger MP4", "Quitter"]
    selected = 0

    def draw_menu(stdscr):
        nonlocal selected
        curses.curs_set(0)  # Désactiver le curseur
        stdscr.clear()
        stdscr.refresh()

        while True:
            stdscr.clear()
            stdscr.addstr(0, 5, "🎵 YouTube Downloader - Sélectionnez une option", curses.A_BOLD)

            for i, option in enumerate(options):
                if i == selected:
                    stdscr.addstr(i + 2, 5, f"> {option}", curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 2, 5, f"  {option}")

            key = stdscr.getch()

            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(options) - 1:
                selected += 1
            elif key in [10, 13]:  # Touche "Entrée"
                return options[selected]

    while True:
        choice = curses.wrapper(draw_menu)

        if choice == "Télécharger MP3":
            url = input("🔗 Entrez l'URL YouTube : ")
            downloaded_file = download_youtube(url, "mp3")
            thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
            add_album_art(downloaded_file, thumbnail_file)
            print(f"✅ Téléchargement terminé : {downloaded_file}\n")

        elif choice == "Télécharger MP4":
            url = input("🔗 Entrez l'URL YouTube : ")
            downloaded_file = download_youtube(url, "mp4")
            print(f"✅ Téléchargement terminé : {downloaded_file}\n")

        elif choice == "Quitter":
            print("👋 Au revoir !")
            break

# Démarrer le menu interactif
if __name__ == "__main__":
    menu()
