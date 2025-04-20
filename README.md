# Downloader-YouTube 🎵🎥

A Python-based web application that allows downloading YouTube videos and audio in various formats (MP4, MP3, etc.).
There is a clean and simple web interface for an improved user experience.

✅ Download videos in MP4 (best available quality)
✅ Download audio in MP3 (192 kbps) with embedded thumbnail
✅ Simple and intuitive web interface

# 📥 Installation

## 1️⃣ Install Python (if not installed)

Download and install Python 3.7 or later from python.org.
Make sure to check "Add Python to PATH" during installation.

## 2️⃣ Install Dependencies

Run the following command in the project folder:

```bash
pip install -r requirements.txt
```

## 3️⃣ Install FFmpeg

FFmpeg is required for merging MP4 and converting MP3.
* Download it from [FFmpeg](https://ffmpeg.org/download.html) official site.
* Add it to system PATH if not already accessible.

# 🛠 Usage

Run the application:

```bash
python main.py
```

Once running, open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

Paste the YouTube URL, choose the format (MP3 or MP4), and download your file in one click!

# 📁 Project Structure

📁 Downloader-YouTube/
│
├── 📄 main.py                → Flask app initialization and config loading
├── 📄 routes.py              → API routes and download task management
├── 📄 utils.py               → Core utilities: download, validation, tagging
│
├── 📄 .env                   → Environment variables (secret key, paths)
├── 📄 requirements.txt       → Project dependencies (Flask, yt-dlp, etc.)
├── 📄 README.md              → Project documentation
│
├── 📂 templates/             → Server-rendered HTML files
│   └── index.html            → Main frontend interface
│
├── 📂 static/                → Static frontend assets
│   ├── styles.css            → App styling
│   └── scripts.js            → Client-side logic (progress, status, messages)
│
└── 📂 tmp/                   → Temporary download storage (auto-created)

# 📝 Changelog

## 0.0.4
- Refactored the code to be more modular  
- Increased front-end/back-end communication
- Enhanced security with .env configuration

## 0.0.3
- Tree-structured code and files
- Switched to a simple and clean web-based UI.
- Improved user experience

## 0.0.2
- Added a complete Readme file
- Added an interactive menu with keyboard navigation
- Improved user experience

## 0.0.1
- Created initial Python script that performs the download

# 👤 Author

@djayatm