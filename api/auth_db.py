import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "auth.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_credentials(email: str, password_hash: str):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO credentials (email, password_hash)
        VALUES (?, ?)
    """, (email.lower().strip(), password_hash))
    conn.commit()
    conn.close()

def get_credentials(email: str) -> str | None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password_hash FROM credentials WHERE email = ?
    """, (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Initialize on import
init_db()
