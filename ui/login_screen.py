import customtkinter as ctk
from auth.auth_manager import AuthManager
from ui.styles import *


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_go_to_register):
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_login_success  = on_login_success
        self.on_go_to_register = on_go_to_register
        self.auth = AuthManager()
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.configure(width=420, height=520)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text="💪 FitTrack",
                     font=FONT_TITLE, text_color=COLORS["accent"]).pack(pady=(40, 4))
        ctk.CTkLabel(card, text="Sign in to your account",
                     font=FONT_BODY, text_color=COLORS["text_sub"]).pack(pady=(0, 24))

        self.username = ctk.CTkEntry(card, placeholder_text="Username",
                                     width=320, height=44, font=FONT_BODY)
        self.username.pack(pady=6)

        self.password = ctk.CTkEntry(card, placeholder_text="Password",
                                     width=320, height=44, font=FONT_BODY, show="●")
        self.password.pack(pady=6)
        self.password.bind("<Return>", lambda e: self._login())

        self.error_lbl = ctk.CTkLabel(card, text="",
                                       font=FONT_SMALL, text_color=COLORS["error"])
        self.error_lbl.pack(pady=(4, 0))

        self.login_btn = ctk.CTkButton(
            card, text="Sign In", width=320, height=44, font=FONT_H3,
            command=self._login,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000"
        )
        self.login_btn.pack(pady=(8, 6))

        ctk.CTkLabel(card, text="─────────  or  ─────────",
                     font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(pady=8)

        ctk.CTkButton(
            card, text="Create an account", width=320, height=44, font=FONT_BODY,
            command=self.on_go_to_register,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"], text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        ).pack(pady=6)

    def _login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            self.error_lbl.configure(text="Please fill in all fields.")
            return
        self.login_btn.configure(state="disabled", text="Signing in...")
        ok, result = self.auth.login_user(username, password)
        if ok:
            self.error_lbl.configure(text="")
            self.on_login_success(result)
        else:
            self.error_lbl.configure(text=result)
            self.login_btn.configure(state="normal", text="Sign In")
