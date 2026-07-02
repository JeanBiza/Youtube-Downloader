import sqlite3
import os

DB_PATH = os.path.join(os.path.expanduser("~"), ".ytdownloader.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            formato TEXT,
            calidad TEXT,
            destination TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_download(title: str, url: str, formato: str, calidad: str, destination: str, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (title, url, formato, calidad, destination, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, url, formato, calidad, destination, timestamp))
    conn.commit()
    conn.close()

def get_history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, url, formato, calidad, destination, timestamp
        FROM history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()