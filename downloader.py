from yt_dlp import YoutubeDL
import yt_dlp
from urllib.request import urlopen
from PIL import Image
import io
import re
import os
import database
import datetime

def is_valid_youtube_url(url: str) -> bool:
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id_pattern = r'(v=|youtu\.be/)[a-zA-Z0-9_-]+'
        if re.search(video_id_pattern, url):
            return True
    return False

def get_downloads_folder() -> str:
    return os.path.join(os.path.expanduser("~"), "Downloads")

def is_playlist_url(url: str) -> bool:
    return 'list=' in url

def fetch_video_info(url: str) -> dict:
    opts = {
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Title not available'),
                'video_id': re.search(r"(v=|youtu\.be/)([a-zA-Z0-9_-]+)", url).group(2)
            }
    except yt_dlp.utils.DownloadError:
        raise ValueError("Could not fetch video info. The video may be private or unavailable.")
    except Exception:
        raise ValueError("Unexpected error fetching video info.")


def fetch_thumbnail(video_id: str) -> Image.Image:
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    image_data = urlopen(thumbnail_url).read()
    image = Image.open(io.BytesIO(image_data))
    return image.resize((480, 270))


def download_video(url: str, formato: str, destination_folder: str, on_progress, on_finish, on_error, calidad: str = "best", download_playlist: bool = False):
    title_cache = {'value': url}

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            progress = d.get('downloaded_bytes', 0) / total * 100
            speed = d.get('speed')
            speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
            on_progress(progress, speed_str)
        if d['status'] == 'finished':
            info = d.get('info_dict', {})
            title_cache['value'] = info.get('title', url)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            database.add_download(title_cache['value'], url, formato, calidad, destination_folder, timestamp)
            on_finish()

    common_opts = {
        'progress_hooks': [progress_hook],
        'noplaylist': not download_playlist,
        'yes_playlist': download_playlist,
        'overwrites': True,
    }

    if not download_playlist:
        common_opts['extractor_args'] = {'youtube': {'player_client': ['tv_embedded']}}

    outtmpl = f'{destination_folder}/%(playlist_title)s/%(title)s.%(ext)s' if download_playlist else f'{destination_folder}/%(title)s.%(ext)s'

    if formato.lower() == "mp4":
        if calidad == "best":
            format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
        else:
            height = calidad.replace("p", "")
            format_str = f'bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[height<={height}]'

        options = {
            **common_opts,
            'format': format_str,
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
        }
    elif formato.lower() == "mp3":
        options = {
            **common_opts,
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        on_error(f"Unsupported format: {formato}")
        return

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        error = str(e)
        if 'Requested format is not available' in error:
            on_error("The selected quality is not available for this video. Try a lower quality.")
        elif 'Private video' in error:
            on_error("This video is private and cannot be downloaded.")
        elif 'Video unavailable' in error:
            on_error("This video is unavailable.")
        elif 'confirm your age' in error:
            on_error("This video requires age verification and cannot be downloaded.")
        else:
            on_error(f"Download error: {e}")
    except yt_dlp.utils.ExtractorError as e:
        on_error(f"Could not extract video info: {e}")
    except Exception as e:
        on_error(f"Unexpected error: {e}")