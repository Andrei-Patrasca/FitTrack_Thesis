import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fittrack.db")


@contextmanager
def db_conn():
    """ commits on success, rolls back on error, always closes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database():
    with db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                username         TEXT    NOT NULL UNIQUE,
                email            TEXT    NOT NULL,
                password         TEXT    NOT NULL,
                reminder_time    TEXT    DEFAULT NULL,
                reminder_enabled INTEGER DEFAULT 0
            )
        """)
        # Safe migrations
        for col, typedef in [
            ("reminder_time",    "TEXT    DEFAULT NULL"),
            ("reminder_enabled", "INTEGER DEFAULT 0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {typedef}")
            except Exception:
                pass

        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                date       TEXT    NOT NULL,
                start_time TEXT    NOT NULL,
                end_time   TEXT    DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exercise_sets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise   TEXT    NOT NULL,
                reps       INTEGER NOT NULL,
                timestamp  TEXT    NOT NULL,
                FOREIGN KEY (workout_id) REFERENCES workouts(id)
            )
        """)
    print("Database initialized.")
