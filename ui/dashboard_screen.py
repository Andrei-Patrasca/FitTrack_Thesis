import customtkinter as ctk
from ui.styles import *


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_start_workout,
                 on_view_history, on_account_settings, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user                = user
        self.on_start_workout    = on_start_workout
        self.on_view_history     = on_view_history
        self.on_account_settings = on_account_settings
        self.on_logout           = on_logout
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top bar
        top = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=56)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text="💪 FitTrack",
                     font=FONT_H2, text_color=COLORS["accent"]).grid(
            row=0, column=0, padx=20, pady=10)
        ctk.CTkLabel(top, text=f"Welcome back, {self.user['username']} 👋",
                     font=FONT_BODY, text_color=COLORS["text_sub"]).grid(
            row=0, column=1, padx=20, pady=10)
        ctk.CTkButton(
            top, text="Logout", width=100, height=34, font=FONT_SMALL,
            command=self.on_logout,
            fg_color="transparent", border_width=1,
            border_color=COLORS["error"], text_color=COLORS["error"],
            hover_color="#4a0000"
        ).grid(row=0, column=2, padx=20, pady=10)

        # Center
        center = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        center.grid(row=1, column=0, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(center, fg_color=COLORS["bg"])
        inner.grid(row=0, column=0)

        ctk.CTkLabel(inner, text="FitTrack",
                     font=FONT_TITLE, text_color=COLORS["accent"]).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="Track your reps. Build your strength.",
                     font=FONT_BODY, text_color=COLORS["text_sub"]).pack(pady=(0, 40))

        ctk.CTkButton(
            inner, text="🏋️   Start Workout",
            width=360, height=64, font=("Segoe UI", 18, "bold"),
            command=self.on_start_workout,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", corner_radius=12
        ).pack(pady=8)

        for text, cmd in [
            ("📋   View History",     self.on_view_history),
            ("⚙️   Account Settings", self.on_account_settings),
        ]:
            ctk.CTkButton(
                inner, text=text, width=360, height=52, font=FONT_H3, command=cmd,
                fg_color="transparent", border_width=1,
                border_color=COLORS["accent"], text_color=COLORS["accent"],
                hover_color=COLORS["accent_dark"], corner_radius=12
            ).pack(pady=8)
