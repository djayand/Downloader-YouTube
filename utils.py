import os
import re
import subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import yt_dlp

def is_valid_url(url: str) -> bool:
    yt_regex = re.compile(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$')
    return bool(yt_regex.match(url))

def is_ffmpeg_installed() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def clean_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube(url: str, output_format: str, download_folder: str) -> str:
    if not is_ffmpeg_installed():
        return None

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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = clean_filename(info_dict.get('title', 'unknown'))
            return os.path.join(download_folder, f"{title}.{'mp3' if output_format == 'mp3' else 'mp4'}")
    except Exception:
        return None

def add_album_art(mp3_file: str, thumbnail_file: str):
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
