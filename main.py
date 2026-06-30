import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk
import threading
import downloader


def display_thumbnail(event=None):
    url = url_entry.get()
    if not downloader.is_valid_youtube_url(url):
        preview_label.config(text="Invalid URL", fg="red", font=("Helvetica", 14))
        thumbnail_label.config(image="", text="", width=10, height=10)
        return
    preview_label.config(text="Loading preview...", fg="black", font=("Helvetica", 14))
    threading.Thread(target=load_video_info, args=(url,), daemon=True).start()


def load_video_info(url):
    try:
        info = downloader.fetch_video_info(url)
        image = downloader.fetch_thumbnail(info['video_id'])
        root.after(0, update_ui, info['title'], image)
    except Exception as e:
        root.after(0, preview_label.config, {"text": "Error loading preview", "fg": "red"})


def update_ui(title, image):
    preview_label.config(text=title, fg="black", font=("Helvetica", 9))
    thumbnail_image = ImageTk.PhotoImage(image)
    thumbnail_label.config(image=thumbnail_image, text="", bg="white", width=500, height=200)
    thumbnail_label.image = thumbnail_image
    thumbnail_label.pack(padx=10, pady=5)


def on_download():
    url = url_entry.get()
    formato = format_combobox.get()
    destination = folder_path.get()

    error_label.config(text="")
    result_label.config(text="")

    if not url:
        error_label.config(text="Please enter a URL", fg="red")
        return
    if not downloader.is_valid_youtube_url(url):
        error_label.config(text="Please enter a valid YouTube URL", fg="red")
        return
    if not destination:
        error_label.config(text="Please select a destination folder", fg="red")
        return

    progress_bar.pack(padx=10, pady=10)
    progress_bar['value'] = 0
    result_label.config(text="Downloading...")

    threading.Thread(
        target=downloader.download_video,
        args=(url, formato, destination, on_progress, on_finish, on_error),
        daemon=True
    ).start()


def on_progress(progress):
    root.after(0, lambda: progress_bar.config(value=progress))


def on_finish():
    root.after(0, _finish_ui)


def _finish_ui():
    progress_bar['value'] = 100
    progress_bar.pack_forget()
    result_label.config(text="Download complete!", fg="green")
    url_entry.delete(0, tk.END)
    preview_label.config(text="Preview", fg="black")
    thumbnail_label.config(image="", text="", width=10, height=10)


def on_error(message):
    root.after(0, lambda: result_label.config(text=f"Error: {message}", fg="red"))
    root.after(0, progress_bar.pack_forget)


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)


def clear_url():
    url_entry.delete(0, tk.END)
    preview_label.config(text="Preview", fg="black")
    thumbnail_label.config(image="", text="", width=10, height=10)


def center_window(window):
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2) - 50
    window.geometry(f"{w}x{h}+{x}+{y}")


# --- UI ---
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x600")
root.resizable(False, False)

url_label = tk.Label(root, text="Enter video URL:")
url_label.pack(padx=10, pady=5)

url_entry_frame = tk.Frame(root)
url_entry_frame.pack(padx=10, pady=5)

url_entry = tk.Entry(url_entry_frame, width=40)
url_entry.pack(side=tk.LEFT, padx=5)
url_entry.bind("<FocusOut>", display_thumbnail)
url_entry.bind("<Return>", display_thumbnail)

clear_button = tk.Button(url_entry_frame, text="Clear", command=clear_url)
clear_button.pack(side=tk.LEFT)

error_label = tk.Label(root, text="", fg="red")
error_label.pack(padx=10, pady=5)

format_label = tk.Label(root, text="Choose format:")
format_label.pack(padx=10, pady=5)

format_combobox = ttk.Combobox(root, values=["MP4", "MP3"], state="readonly")
format_combobox.set("MP4")
format_combobox.pack(padx=10, pady=5)

folder_path = tk.StringVar()
folder_path.set(downloader.get_downloads_folder())

folder_button = tk.Button(root, text="Select destination folder", command=choose_folder)
folder_button.pack(padx=10, pady=5)

folder_label = tk.Label(root, textvariable=folder_path)
folder_label.pack(padx=10, pady=5)

download_button = tk.Button(root, text="Download", command=on_download)
download_button.pack(padx=10, pady=20)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.pack(padx=10, pady=5)

progress_bar = ttk.Progressbar(root, length=300, mode='determinate', maximum=100)
progress_bar.pack_forget()

preview_label = tk.Label(root, text="Preview")
preview_label.pack(fill="both", expand=True)

thumbnail_label = tk.Label(root, text="", width=1, height=1)
thumbnail_label.pack_forget()

if __name__ == "__main__":
    center_window(root)
    root.mainloop()