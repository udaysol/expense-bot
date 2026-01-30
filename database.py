import sqlite3
from pathlib import Path

DB_PATH = Path("data/expenses.db")

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        trip_name TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        start_time TEXT,
        end_time TEXT
    );

    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER NOT NULL,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER NOT NULL,
        description TEXT,
        total_amount INTEGER NOT NULL,
        paid_by TEXT NOT NULL,
        split_type TEXT NOT NULL,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS expense_splits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_id INTEGER NOT NULL,
        person TEXT NOT NULL,
        amount INTEGER NOT NULL
    );
    """)

    conn.commit()
    conn.close()
