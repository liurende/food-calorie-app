import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "calorie.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS food_density (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            density_g_cm3 REAL NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_per_100g REAL,
            carbs_per_100g REAL,
            fat_per_100g REAL,
            category TEXT
        );

        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
            image_paths TEXT,
            total_calories REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            weight_g REAL NOT NULL,
            calories REAL NOT NULL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            confidence REAL
        );
    """)
    conn.commit()
    conn.close()
