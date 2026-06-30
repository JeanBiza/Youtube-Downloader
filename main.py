import customtkinter as ctk
from PIL import ImageTk
import threading
import downloader

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def display_thumbnail(event=None):
    url = url_entry.get()
    if not downloader.is_valid_youtube_url(url):
        preview_label.configure(text="Invalid URL", text_color="red")
        thumbnail_label.configure(image="", text="")
        return
    preview_label.configure(text="Loading preview...", text_color="gray")
    threading.Thread(target=load_video_info, args=(url,), daemon=True).start()


def load_video_info(url):
    try:
        info = downloader.fetch_video_info(url)
        image = downloader.fetch_thumbnail(info['video_id'])
        root.after(0, update_ui, info['title'], image)
    except Exception:
        root.after(0, lambda: preview_label.configure(text="Error loading preview", text_color="red"))


def update_ui(title, image):
    preview_label.configure(text=title, text_color="white")
    ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(480, 270))
    thumbnail_label.configure(image=ctk_image, text="")
    thumbnail_label.image = ctk_image


def on_download():
    url = url_entry.get()
    formato = format_combobox.get()
    destination = folder_path.get()

    error_label.configure(text="")
    result_label.configure(text="")

    if not url:
        error_label.configure(text="Please enter a URL", text_color="red")
        return
    if not downloader.is_valid_youtube_url(url):
        error_label.configure(text="Please enter a valid YouTube URL", text_color="red")
        return
    if not destination:
        error_label.configure(text="Please select a destination folder", text_color="red")
        return

    progress_bar.pack(padx=20, pady=10)
    progress_bar.set(0)
    result_label.configure(text="Downloading...", text_color="gray")
    download_button.configure(state="disabled")

    calidad = quality_combobox.get()

    threading.Thread(
        target=downloader.download_video,
        args=(url, formato, destination, on_progress, on_finish, on_error, calidad),
        daemon=True
    ).start()


def on_progress(progress):
    root.after(0, lambda: progress_bar.set(progress / 100))


def on_finish():
    root.after(0, _finish_ui)


def _finish_ui():
    progress_bar.set(1)
    progress_bar.pack_forget()
    result_label.configure(text="Download complete!", text_color="green")
    download_button.configure(state="normal")
    url_entry.delete(0, ctk.END)
    preview_label.configure(text="Preview")
    thumbnail_label.configure(image="", text="")


def on_error(message):
    root.after(0, lambda: result_label.configure(text=f"Error: {message}", text_color="red"))
    root.after(0, progress_bar.pack_forget)
    root.after(0, lambda: download_button.configure(state="normal"))


def choose_folder():
    import tkinter.filedialog as fd
    folder = fd.askdirectory()
    if folder:
        folder_path.set(folder)
        folder_label.configure(text=folder)


def clear_url():
    url_entry.delete(0, ctk.END)
    preview_label.configure(text="Preview", text_color="white")
    thumbnail_label.configure(image="", text="")


def center_window(window):
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2) - 50
    window.geometry(f"{w}x{h}+{x}+{y}")


#  UI
root = ctk.CTk()
root.title("YouTube Downloader")
root.geometry("520x720")
root.resizable(False, False)

title_label = ctk.CTkLabel(root, text="YouTube Downloader", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=(20, 10))

url_frame = ctk.CTkFrame(root, fg_color="transparent")
url_frame.pack(padx=20, pady=5, fill="x")

url_entry = ctk.CTkEntry(url_frame, placeholder_text="Enter YouTube URL...", width=380)
url_entry.pack(side="left", padx=(0, 5))
url_entry.bind("<FocusOut>", display_thumbnail)
url_entry.bind("<Return>", display_thumbnail)

clear_button = ctk.CTkButton(url_frame, text="Clear", width=70, command=clear_url)
clear_button.pack(side="left")

error_label = ctk.CTkLabel(root, text="", text_color="red")
error_label.pack(pady=2)

format_label = ctk.CTkLabel(root, text="Format:")
format_label.pack(pady=(10, 2))

format_combobox = ctk.CTkComboBox(root, values=["MP4", "MP3"], state="readonly", width=200)
format_combobox.set("MP4")
format_combobox.pack(pady=5)

quality_label = ctk.CTkLabel(root, text="Quality (MP4 only):")
quality_label.pack(pady=(10, 2))

quality_combobox = ctk.CTkComboBox(root, values=["best", "1080p", "720p", "480p", "360p"], state="readonly", width=200)
quality_combobox.set("best")
quality_combobox.pack(pady=5)

folder_button = ctk.CTkButton(root, text="Select destination folder", command=choose_folder)
folder_button.pack(pady=5)

folder_path = ctk.StringVar()
folder_path.set(downloader.get_downloads_folder())

folder_label = ctk.CTkLabel(root, text=downloader.get_downloads_folder(), text_color="gray", wraplength=460)
folder_label.pack(pady=2)

download_button = ctk.CTkButton(root, text="Download", command=on_download, width=200, height=40,
                                font=ctk.CTkFont(size=14, weight="bold"))
download_button.pack(pady=20)

result_label = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=13))
result_label.pack(pady=5)

progress_bar = ctk.CTkProgressBar(root, width=460)
progress_bar.pack_forget()

preview_label = ctk.CTkLabel(root, text="Preview", text_color="gray")
preview_label.pack(pady=(10, 5))

thumbnail_label = ctk.CTkLabel(root, text="")
thumbnail_label.pack()

if __name__ == "__main__":
    center_window(root)
    root.mainloop()