# YouTube Downloader

A desktop application to download YouTube videos and audio built with Python, yt-dlp and customtkinter.

## Features

- Download videos as **MP4** or audio as **MP3**
- **Quality selector** for MP4 (Best, 1080p, 720p, 480p, 360p)
- **Playlist support** — detects playlist URLs and asks whether to download the full playlist or just the video
- **Video preview** — shows thumbnail and title when a URL is entered
- **Progress bar** with download percentage and speed
- **Download history** stored locally with SQLite
- Modern dark UI with customtkinter

## Requirements

- Python 3.11+
- ffmpeg installed on the system

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/JeanBiza/youtube-downloader.git
cd youtube-downloader
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv

source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

**3. Install ffmpeg**
```bash
# Arch / EndeavourOS
sudo pacman -S ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Extract the zip and add the bin/ folder to your system PATH
```

**4. Run the app**
```bash
python main.py
```

## Usage

1. Paste a YouTube URL in the input field and press Enter or click away — the thumbnail and title will load automatically
2. Select the output format (MP4 or MP3)
3. If MP4, choose the desired quality
4. Select the destination folder (defaults to ~/Downloads)
5. Click **Download**
6. If the URL contains a playlist, you'll be asked whether to download the full playlist or just the current video

## Project structure

```
youtube-downloader/
├── main.py          # UI built with customtkinter
├── downloader.py    # Download logic using yt-dlp
├── database.py      # SQLite download history
├── requirements.txt
└── .gitignore
```

## Stack

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — modern dark UI
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube extraction and download
- [Pillow](https://python-pillow.org/) — thumbnail image processing
- SQLite — local download history persistence