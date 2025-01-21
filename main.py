from yt_dlp import YoutubeDL
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
from urllib.request import urlopen
from PIL import Image, ImageTk
import io
import re
import threading
import os
import subprocess


def actualizar_yt_dlp():
    try:
        subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=True)
        print("yt_dlp se ha actualizado correctamente.")
    except Exception as e:
        print(f"Error al actualizar yt_dlp: {e}")


def display_thumbnail(event=None):
    url = url_entry.get()
    if not is_valid_youtube_url(url):
        preview_label.config(text="URL no válida", fg="red", font=("Helvetica", 14))
        thumbnail_label.config(image="", text="", width=10, height=10)
        return
    
    preview_label.config(text="Cargando vista previa",fg="black", font=("Helvetica", 14))
    threading.Thread(target=fetch_video_info, args=(url,)).start()

def fetch_video_info(url):
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Título no disponible')
        
        root.after(0, update_ui, video_title, url)

    except Exception as e:
        pass

def update_ui(video_title, url):    
    preview_label.config(text=video_title, fg="black", font=("Helvetica", 9))

    video_id = re.search(r"(v=|youtu\.be/)([a-zA-Z0-9_-]+)", url).group(2)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    try:
        image_data = urlopen(thumbnail_url).read()
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((480, 270)) 
        thumbnail_image = ImageTk.PhotoImage(image)

        thumbnail_label.config(image=thumbnail_image, text="", bg="white", font=("Helvetica", 16), width=500, height=200)
        thumbnail_label.image = thumbnail_image
        thumbnail_label.pack(padx=10, pady=5)

    except Exception as e:
        thumbnail_label.config(image="", text="Error al cargar la miniatura", bg="gray", width=480, height=270)
        print(f"Error al cargar miniatura: {e}")


def download():
    result_label.config(text="")

    url = url_entry.get()
    formato = format_combobox.get()
    destination_folder = folder_path.get()

    if not url:
        error_label.config(text="Debe ingresar una URL", fg="red")
        return
    if is_valid_youtube_url(url) == False:
        error_label.config(text="Ingrese una URL válida de YouTube", fg="red")
        return
    if not destination_folder:
        error_label.config(text="Debe seleccionar una carpeta de destino", fg="red")
        return
    
    error_label.config(text="")

    progress_bar.pack(padx=10, pady=10)
    progress_bar['value'] = 0
    progress_bar['maximum'] = 100 
    progress_bar.start()

    threading.Thread(target=download_archive, args=(url, formato, destination_folder)).start()

def get_file_name(url, formato, destination_folder):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' if formato.lower() == "mp4" else 'bestaudio/best',
        'outtmpl': f'{destination_folder}/%(title)s.%(ext)s'
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return os.path.join(destination_folder, f"{info_dict['title']}.{formato.lower()}")

def download_archive(url, formato, destination_folder):
    def progress_hook(d):
        if d['status'] == 'downloading':
            progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
            root.after(0, update_progress_bar, progress)
        if d['status'] == 'finished':
            root.after(0, finish_download)

    options = {}
    
    if formato.lower() == "mp4":
            options = {
            'format' : 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl' : f'{destination_folder}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks' : [progress_hook],
            'noplaylist': True,
            'overwrites': True,

        }
    
    if formato.lower() == "mp3":
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{destination_folder}/%(title)s.%(ext)s',
            'postprocessors': [
                {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  
                'preferredquality': '192',
                }
            ],
            'progress_hooks' : [progress_hook],
            'noplaylist': True,
            'overwrites': True,
        }

    try:
        with YoutubeDL(options) as ydl:
            result_label.config(text="Espere un momento.")
            ydl.download([url])
            result_label.config(text="Archivo descargado correctamente.")
            url_entry.delete(0, tk.END)
    except Exception as e:
            print(f'ha ocurrido un error : {e}')

def is_valid_youtube_url(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id_pattern = r'(v=|youtu\.be/)[a-zA-Z0-9_-]+'
        if re.search(video_id_pattern, url):
            return True
    return False

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def choose_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

def update_progress_bar(progress):
    progress_bar['value'] = progress
    root.update_idletasks()

def finish_download():
    progress_bar['value'] = 100
    root.update_idletasks()
    progress_bar.pack_forget()  

def clear_url():
    url_entry.delete(0, tk.END)
    preview_label.config(text="Vista previa", fg="black")
    thumbnail_label.config(image="", text="", width=10, height=10)

def center_window(window):
    offset_up = 50
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height() 
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2) 
    y = (screen_height // 2) - (height // 2) - offset_up
    window.geometry(f"{width}x{height}+{x}+{y}") 

root = tk.Tk()
root.title("Descargador de Youtube")
root.geometry("400x600")
root.resizable(False, False)


url_label = tk.Label(root, text="Ingresa la URL del video:")
url_label.pack(padx=10, pady=5)

url_entry_frame = tk.Frame(root)
url_entry_frame.pack(padx=10, pady=5)

url_entry = tk.Entry(url_entry_frame, width=40)
url_entry.pack(side=tk.LEFT, padx=5)
url_entry.bind("<FocusOut>", display_thumbnail)
url_entry.bind("<Return>", display_thumbnail) 

clear_button = tk.Button(url_entry_frame, text="Limpiar", command=clear_url)
clear_button.pack(side=tk.LEFT)

error_label = tk.Label(root, text="")
error_label.pack(padx=10, pady=5)

format_label = tk.Label(root, text="Elige el formato:")
format_label.pack(padx=10, pady=5)

format_combobox = ttk.Combobox(root, values=["MP4", "MP3"], state="readonly")
format_combobox.set("MP4")
format_combobox.pack(padx=10, pady=5)

folder_path = tk.StringVar() 
folder_path.set(get_downloads_folder())
folder_button = tk.Button(root, text="Seleccionar Carpeta de guardado", command=choose_folder)
folder_button.pack(padx=10, pady=5)

folder_label = tk.Label(root, textvariable=folder_path)
folder_label.pack(padx=10, pady=5)

download_button = tk.Button(root, text="Descargar", command=download)
download_button.pack(padx=10, pady=20)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.pack(padx=10, pady=5)  

progress_bar = ttk.Progressbar(root, length=300, mode='determinate', maximum=100)
progress_bar.pack_forget()

preview_label = tk.Label(root, text="Vista previa")
preview_label.pack(fill="both", expand=True)

thumbnail_label = tk.Label(root, text="", width=1, height=1)
thumbnail_label.pack_forget()

if __name__ == "__main__":
    actualizar_yt_dlp()
    center_window(root)
    root.mainloop()
