from flask import Flask, request, render_template, send_file
import yt_dlp
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

app = Flask(__name__)

# Fonction de téléchargement
def download_youtube(url, output_format):
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
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
                {"key": "EmbedThumbnail"}
            ],
            "writethumbnail": True,
            "postprocessor_args": ["-id3v2_version", "3"]
        })
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'unknown')
        return f"{title}.{output_format}"

# Ajout de l'album art
def add_album_art(mp3_file: str, thumbnail_file: str):
    if not os.path.exists(thumbnail_file):
        print("Thumbnail not found, skipping album art.")
        return

    audio = MP3(mp3_file, ID3=ID3)
    img = Image.open(thumbnail_file)
    img = img.resize((500, 500))
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
    print(f"✅ Album art added to {mp3_file}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_choice = request.form.get('format')
        if url:
            downloaded_file = download_youtube(url, format_choice)
            if format_choice == "mp3":
                thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
                add_album_art(downloaded_file, thumbnail_file)
            return send_file(downloaded_file, as_attachment=True)
    return render_template('index.html', success=False)

if __name__ == "__main__":
    app.run(debug=True)