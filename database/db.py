import sqlite3
from werkzeug.security import generate_password_hash
import os

DATABASE = "spendly.db"


def get_db():
    """Open connection to SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create database tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """Insert sample data for development (idempotent)."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] > 0:
        conn.close()
        return

    # Insert demo user
    demo_password_hash = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", demo_password_hash)
    )
    user_id = cursor.lastrowid

    # Insert sample expenses
    sample_expenses = [
        (user_id, 45.50, "Food", "2026-04-10", "Lunch at cafe"),
        (user_id, 30.00, "Transport", "2026-04-09", "Gas for car"),
        (user_id, 120.00, "Bills", "2026-04-08", "Electric bill"),
        (user_id, 25.99, "Health", "2026-04-07", "Pharmacy"),
        (user_id, 55.00, "Entertainment", "2026-04-06", "Movie tickets"),
        (user_id, 89.99, "Shopping", "2026-04-05", "New shoes"),
        (user_id, 15.50, "Food", "2026-04-04", "Coffee"),
        (user_id, 40.00, "Other", "2026-04-03", "Miscellaneous"),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )

    conn.commit()
    conn.close()
