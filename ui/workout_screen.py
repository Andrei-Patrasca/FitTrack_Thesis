import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
from ai.pose_estimator import PoseEstimator
from ai.angle_calculator import AngleCalculator
from ai.rep_counter import RepCounter
from ai.exercise_classifier_cnn import ExerciseClassifierCNN
from database.workout_manager import WorkoutManager
from ui.styles import *

_EXERCISE_NAMES = {
    "bicep_curl": "💪 Bicep Curl",
    "squat":      "🦵 Squat",
    "pushup":     "🏋️ Push-up",
}
_DISPLAY_NAMES = {
    "bicep_curl": "Bicep Curl",
    "squat":      "Squat",
    "pushup":     "Push-up",
}


class WorkoutScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_finish):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user            = user
        self.on_finish       = on_finish
        self.estimator       = PoseEstimator()
        self.calculator      = AngleCalculator()
        self.counter         = RepCounter()
        self.classifier      = ExerciseClassifierCNN()
        self.workout_manager = WorkoutManager(user["id"])
        self.is_running      = False
        self.is_paused       = False
        self.cap             = None
        self.start_time      = None
        self.last_exercise   = "unknown"
        self.last_rep_counts = {"bicep_curl": 0, "squat": 0, "pushup": 0}
        self.log_entries     = []
        self._build()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self._build_left()
        self._build_center()
        self._build_right()

    def _build_left(self):
        left = ctk.CTkFrame(self, fg_color=COLORS["surface"],
                            corner_radius=12, width=180)
        left.grid(row=0, column=0, sticky="ns", padx=(12, 6), pady=12)
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="Controls",
                     font=FONT_H3, text_color=COLORS["accent"]).pack(pady=(24, 16))

        self.start_btn = ctk.CTkButton(
            left, text="▶  Start", width=148, height=52, font=FONT_H3,
            command=self._start_workout,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000"
        )
        self.start_btn.pack(pady=6)

        self.pause_btn = ctk.CTkButton(
            left, text="⏸  Pause", width=148, height=52, font=FONT_H3,
            command=self._toggle_pause,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"], text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        )
        self.finish_btn = ctk.CTkButton(
            left, text="✔  Finish", width=148, height=52, font=FONT_H3,
            command=self._finish_workout,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"], text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        )

        ctk.CTkLabel(left, text="", fg_color="transparent").pack(expand=True)
        ctk.CTkLabel(left, text="Duration",
                     font=FONT_SMALL, text_color=COLORS["text_sub"]).pack()
        self.timer_lbl = ctk.CTkLabel(left, text="00:00:00",
                                       font=FONT_ACCENT, text_color=COLORS["accent"])
        self.timer_lbl.pack(pady=(0, 24))

    def _build_center(self):
        center = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        center.grid(row=0, column=1, sticky="nsew", padx=6, pady=12)
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(0, weight=1)

        self.exercise_lbl = ctk.CTkLabel(
            center, text="Press Start to begin",
            font=FONT_H2, text_color=COLORS["accent"]
        )
        self.exercise_lbl.grid(row=0, column=0, pady=(0, 8))

        self.video_frame = ctk.CTkFrame(center, fg_color="#000000", corner_radius=12)
        self.video_frame.grid(row=1, column=0, sticky="nsew")

        self.video_lbl = ctk.CTkLabel(
            self.video_frame, text="Camera will appear here",
            font=FONT_BODY, text_color=COLORS["text_muted"]
        )
        self.video_lbl.pack(expand=True, fill="both")

        ctk.CTkLabel(center, text="Rep progress",
                     font=FONT_SMALL, text_color=COLORS["text_sub"]).grid(
            row=2, column=0, pady=(8, 2))
        self.progress = ctk.CTkProgressBar(
            center, width=400, height=16,
            progress_color=COLORS["accent"], fg_color=COLORS["surface_alt"]
        )
        self.progress.set(0)
        self.progress.grid(row=3, column=0, pady=(0, 8))

    def _build_right(self):
        right = ctk.CTkFrame(self, fg_color=COLORS["surface"],
                              corner_radius=12, width=220)
        right.grid(row=0, column=2, sticky="ns", padx=(6, 12), pady=12)
        right.grid_propagate(False)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Workout Log",
                     font=FONT_H3, text_color=COLORS["accent"]).grid(
            row=0, column=0, pady=(20, 8))

        self.log_frame = ctk.CTkScrollableFrame(
            right, fg_color=COLORS["surface_alt"], corner_radius=8
        )
        self.log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        ctk.CTkFrame(right, fg_color=COLORS["border"], height=1).grid(
            row=2, column=0, sticky="ew", padx=10)

        totals = ctk.CTkFrame(right, fg_color="transparent")
        totals.grid(row=3, column=0, sticky="ew", padx=12, pady=(8, 20))
        ctk.CTkLabel(totals, text="Totals",
                     font=FONT_H3, text_color=COLORS["text_sub"]).pack(anchor="w")

        self.lbl_curls   = ctk.CTkLabel(totals, text="Bicep Curls:  0",
                                         font=FONT_BODY, text_color=COLORS["text"])
        self.lbl_squats  = ctk.CTkLabel(totals, text="Squats:       0",
                                         font=FONT_BODY, text_color=COLORS["text"])
        self.lbl_pushups = ctk.CTkLabel(totals, text="Push-ups:     0",
                                         font=FONT_BODY, text_color=COLORS["text"])
        for lbl in (self.lbl_curls, self.lbl_squats, self.lbl_pushups):
            lbl.pack(anchor="w", pady=2)

    # ── Workout control ────────────────────────────────────────────────────────
    def _start_workout(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.exercise_lbl.configure(text="❌ Camera not found!")
            return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.workout_manager.start_workout()
        self.start_time = datetime.now()
        self.is_running = True
        self.is_paused  = False

        self.start_btn.pack_forget()
        self.pause_btn.pack(pady=6)
        self.finish_btn.pack(pady=6)

        self._update_frame()
        self._update_timer()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="▶  Resume")
            self.exercise_lbl.configure(text="⏸  Paused")
        else:
            self.pause_btn.configure(text="⏸  Pause")
            self._update_frame()

    def _finish_workout(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self._flush_reps()
        self.workout_manager.finish_workout()
        self.estimator.close()
        self.on_finish()

    def _flush_reps(self):
        for exercise in ("bicep_curl", "squat", "pushup"):
            diff = self.counter.get_count(exercise) - self.last_rep_counts[exercise]
            if diff > 0:
                self.workout_manager.log_set(exercise, diff)
                self.last_rep_counts[exercise] += diff

    # ── Frame loop ─────────────────────────────────────────────────────────────
    def _update_frame(self):
        if not self.is_running or self.is_paused:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.after(33, self._update_frame)
            return

        frame, landmarks = self.estimator.process_frame(frame)
        exercise = self.classifier.classify(landmarks)

        if exercise != "unknown" and exercise != self.last_exercise:
            if self.last_exercise != "unknown":
                self._flush_reps()
            self.last_exercise = exercise
            self.exercise_lbl.configure(
                text=_EXERCISE_NAMES.get(exercise, "Detecting..."))

        progress = 0.0
        if landmarks and exercise != "unknown":
            angle    = self.calculator.get_exercise_angles(landmarks, exercise)
            rep_done = self.counter.process(exercise, angle)
            progress = self.counter.get_progress(exercise, angle)
            if rep_done:
                self._on_rep(exercise)
            if angle is not None:
                cv2.putText(frame, f"{angle:.0f}deg",
                            (10, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (57, 255, 20), 2)

        self.progress.set(progress)

        img = ImageTk.PhotoImage(
            Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        )
        self.video_lbl.configure(image=img, text="")
        self.video_lbl.image = img

        self.after(33, self._update_frame)

    def _on_rep(self, exercise):
        total = self.counter.get_count(exercise)
        self.log_entries.insert(0, f"• {total} × {_DISPLAY_NAMES.get(exercise, exercise)}")

        for w in self.log_frame.winfo_children():
            w.destroy()
        for text in self.log_entries:
            ctk.CTkLabel(self.log_frame, text=text, font=FONT_BODY,
                         text_color=COLORS["text"], anchor="w").pack(anchor="w", pady=2)

        self.lbl_curls.configure(
            text=f"Bicep Curls:  {self.counter.get_count('bicep_curl')}")
        self.lbl_squats.configure(
            text=f"Squats:       {self.counter.get_count('squat')}")
        self.lbl_pushups.configure(
            text=f"Push-ups:     {self.counter.get_count('pushup')}")

    def _update_timer(self):
        if not self.is_running:
            return
        if not self.is_paused and self.start_time:
            elapsed = int((datetime.now() - self.start_time).total_seconds())
            h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
            self.timer_lbl.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self._update_timer)

    def destroy(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        super().destroy()
