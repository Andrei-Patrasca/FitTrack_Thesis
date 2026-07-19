import bcrypt
from database.db import db_conn


class AuthManager:

    def register_user(self, username, email, password):
        if not username or not email or not password:
            return False, "All fields are required."
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            with db_conn() as conn:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, hashed)
                )
            return True, "Registration successful."
        except Exception as e:
            err = str(e)
            if "username" in err: return False, "Username already taken."
            if "email"    in err: return False, "Email already registered."
            return False, f"Database error: {err}"

    def login_user(self, username, password):
        with db_conn() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username=?", (username,)
            ).fetchone()
        if user is None:
            return False, "Username not found."
        if not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return False, "Incorrect password."
        return True, user

    def update_user(self, user_id, username=None, email=None, password=None):
        with db_conn() as conn:
            if username:
                conn.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))
            if email:
                conn.execute("UPDATE users SET email=?    WHERE id=?", (email,    user_id))
            if password:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                conn.execute("UPDATE users SET password=? WHERE id=?", (hashed,   user_id))

    def update_reminder(self, user_id, reminder_time, reminder_enabled):
        with db_conn() as conn:
            conn.execute(
                "UPDATE users SET reminder_time=?, reminder_enabled=? WHERE id=?",
                (reminder_time, 1 if reminder_enabled else 0, user_id)
            )

    def get_user_by_id(self, user_id):
        with db_conn() as conn:
            return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
