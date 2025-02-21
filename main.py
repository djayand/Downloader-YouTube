import os
import yt_dlp
import curses

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

def download_youtube(url: str, output_format: str):
    """
    Downloads a YouTube video in MP4 or extracts audio in MP3 format.

    :param url: YouTube video URL
    :param output_format: "mp4" for video, "mp3" for audio
    :return: Downloaded file path
    """
    output_template = "%(title)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_template,  # Set output file name
        "quiet": False  # Show yt-dlp logs
    }
    
    if output_format == "mp4":
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",  # Get best quality video + audio
            "merge_output_format": "mp4"  # Merge into an MP4 file
        })
    elif output_format == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",  # Download only the best audio
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                },
                {
                    "key": "EmbedThumbnail"  # Add video thumbnail as album art
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
    Adds a thumbnail as album art to an MP3 file.

    :param mp3_file: Path to the MP3 file
    :param thumbnail_file: Path to the thumbnail image
    """
    if not os.path.exists(thumbnail_file):
        print("Thumbnail not found, skipping album art.")
        return

    audio = MP3(mp3_file, ID3=ID3)

    # Resize the image to ensure it is square
    img = Image.open(thumbnail_file)
    img = img.resize((500, 500))  # Resize to 500x500 pixels
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

def menu():
    """
    Displays an interactive menu to choose:
    - Download MP3
    - Download MP4
    - Exit the application
    """
    options = ["Download MP3", "Download MP4", "Exit"]
    selected = 0

    def draw_menu(stdscr):
        nonlocal selected
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        stdscr.refresh()

        while True:
            stdscr.clear()
            stdscr.addstr(0, 5, "🎵 YouTube Downloader - Select an option", curses.A_BOLD)

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
            elif key in [10, 13]:  # Enter key
                return options[selected]

    while True:
        choice = curses.wrapper(draw_menu)

        if choice == "Download MP3":
            url = input("🔗 Enter YouTube URL: ")
            downloaded_file = download_youtube(url, "mp3")
            thumbnail_file = downloaded_file.replace(".mp3", ".jpg")
            add_album_art(downloaded_file, thumbnail_file)
            print(f"✅ Download complete: {downloaded_file}\n")

        elif choice == "Download MP4":
            url = input("🔗 Enter YouTube URL: ")
            downloaded_file = download_youtube(url, "mp4")
            print(f"✅ Download complete: {downloaded_file}\n")

        elif choice == "Exit":
            print("👋 Goodbye!")
            break

# Start the interactive menu
if __name__ == "__main__":
    menu()
