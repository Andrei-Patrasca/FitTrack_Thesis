from database.db import db_conn
from datetime import datetime


class WorkoutManager:
    def __init__(self, user_id):
        self.user_id    = user_id
        self.workout_id = None

    def start_workout(self):
        now = datetime.now()
        with db_conn() as conn:
            cur = conn.execute(
                "INSERT INTO workouts (user_id, date, start_time) VALUES (?, ?, ?)",
                (self.user_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
            )
            self.workout_id = cur.lastrowid
        return self.workout_id

    def log_set(self, exercise, reps):
        if not self.workout_id or reps <= 0:
            return
        with db_conn() as conn:
            conn.execute(
                "INSERT INTO exercise_sets (workout_id, exercise, reps, timestamp) VALUES (?, ?, ?, ?)",
                (self.workout_id, exercise, reps, datetime.now().strftime("%H:%M:%S"))
            )

    def finish_workout(self):
        if not self.workout_id:
            return
        with db_conn() as conn:
            conn.execute(
                "UPDATE workouts SET end_time=? WHERE id=?",
                (datetime.now().strftime("%H:%M:%S"), self.workout_id)
            )

    def get_workouts(self):
        with db_conn() as conn:
            return conn.execute(
                "SELECT id, date, start_time, end_time FROM workouts"
                " WHERE user_id=? ORDER BY date DESC, start_time DESC",
                (self.user_id,)
            ).fetchall()

    def get_sets(self, workout_id):
        with db_conn() as conn:
            return conn.execute(
                "SELECT exercise, reps, timestamp FROM exercise_sets"
                " WHERE workout_id=? ORDER BY id ASC",
                (workout_id,)
            ).fetchall()
