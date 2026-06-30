from yt_dlp import YoutubeDL
from urllib.request import urlopen
from PIL import Image
import io
import re
import os


def is_valid_youtube_url(url: str) -> bool:
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id_pattern = r'(v=|youtu\.be/)[a-zA-Z0-9_-]+'
        if re.search(video_id_pattern, url):
            return True
    return False


def get_downloads_folder() -> str:
    return os.path.join(os.path.expanduser("~"), "Downloads")


def fetch_video_info(url: str) -> dict:
    opts = {
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Title not available'),
            'video_id': re.search(r"(v=|youtu\.be/)([a-zA-Z0-9_-]+)", url).group(2)
        }

def fetch_thumbnail(video_id: str) -> Image.Image:
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    image_data = urlopen(thumbnail_url).read()
    image = Image.open(io.BytesIO(image_data))
    return image.resize((480, 270))


def download_video(url: str, formato: str, destination_folder: str, on_progress, on_finish, on_error, calidad: str = "best"):
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            progress = d.get('downloaded_bytes', 0) / total * 100
            speed = d.get('speed')
            speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
            on_progress(progress, speed_str)
        if d['status'] == 'finished':
            on_finish()

    if formato.lower() == "mp4":
        if calidad == "best":
            format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
        else:
            height = calidad.replace("p", "")
            format_str = f'bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[height<={height}]'

        options = {
            'format': format_str,
            'outtmpl': f'{destination_folder}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'overwrites': True,
            'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
        }
    elif formato.lower() == "mp3":
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{destination_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'overwrites': True,
            'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
        }
    else:
        on_error(f"Unsupported format: {formato}")
        return

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        on_error(str(e))

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        on_error(str(e))