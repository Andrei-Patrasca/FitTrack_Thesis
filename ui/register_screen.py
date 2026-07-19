import customtkinter as ctk
from auth.auth_manager import AuthManager
from auth.email_service import is_valid_email_format, generate_code, send_verification_email
from database.db import db_conn
from ui.styles import *


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, on_register_success, on_go_to_login, on_go_to_verify):
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_register_success = on_register_success
        self.on_go_to_login      = on_go_to_login
        self.on_go_to_verify     = on_go_to_verify
        self.auth = AuthManager()
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.configure(width=420, height=600)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text="💪 FitTrack",
                     font=FONT_TITLE, text_color=COLORS["accent"]).pack(pady=(40, 4))
        ctk.CTkLabel(card, text="Create your account",
                     font=FONT_BODY, text_color=COLORS["text_sub"]).pack(pady=(0, 20))

        self.username = ctk.CTkEntry(card, placeholder_text="Username",
                                     width=320, height=44, font=FONT_BODY)
        self.username.pack(pady=6)
        self.username.bind("<KeyRelease>", self._check_username)

        self.email = ctk.CTkEntry(card, placeholder_text="Email address",
                                  width=320, height=44, font=FONT_BODY)
        self.email.pack(pady=6)

        self.password = ctk.CTkEntry(card, placeholder_text="Password",
                                     width=320, height=44, font=FONT_BODY, show="●")
        self.password.pack(pady=6)

        self.confirm = ctk.CTkEntry(card, placeholder_text="Confirm password",
                                    width=320, height=44, font=FONT_BODY, show="●")
        self.confirm.pack(pady=6)
        self.confirm.bind("<KeyRelease>", lambda e: self._check_match())
        self.confirm.bind("<Return>",     lambda e: self._do_register())

        self.match_lbl = ctk.CTkLabel(card, text="",
                                       font=FONT_SMALL, text_color=COLORS["accent"])
        self.match_lbl.pack(pady=(2, 0))

        self.error_lbl = ctk.CTkLabel(card, text="",
                                       font=FONT_SMALL, text_color=COLORS["error"])
        self.error_lbl.pack(pady=(2, 0))

        self.reg_btn = ctk.CTkButton(
            card, text="Create Account", width=320, height=44, font=FONT_H3,
            command=self._do_register,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000"
        )
        self.reg_btn.pack(pady=(8, 6))

        ctk.CTkLabel(card, text="─────────  or  ─────────",
                     font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(pady=8)

        ctk.CTkButton(
            card, text="Already have an account? Sign in",
            width=320, height=44, font=FONT_BODY, command=self.on_go_to_login,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"], text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        ).pack(pady=6)

    def _check_match(self):
        p1, p2 = self.password.get(), self.confirm.get()
        if not p2:
            self.match_lbl.configure(text="")
            return
        if p1 == p2:
            self.match_lbl.configure(text="✓ Passwords match",       text_color=COLORS["accent"])
        else:
            self.match_lbl.configure(text="✗ Passwords do not match", text_color=COLORS["error"])

    def _do_register(self):
        username = self.username.get().strip()
        email    = self.email.get().strip()
        password = self.password.get()
        confirm  = self.confirm.get()

        if not all([username, email, password, confirm]):
            self.error_lbl.configure(text="Please fill in all fields.")
            return

        with db_conn() as conn:
            if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
                self.error_lbl.configure(text="Username already taken.")
                return

        if not is_valid_email_format(email):
            self.error_lbl.configure(text="Please enter a valid email address.")
            return
        if password != confirm:
            self.error_lbl.configure(text="Passwords do not match.")
            return
        if len(password) < 6:
            self.error_lbl.configure(text="Password must be at least 6 characters.")
            return

        self.reg_btn.configure(state="disabled", text="Sending code...")
        self.error_lbl.configure(text="")

        code = generate_code()
        ok, msg = send_verification_email(email, code)
        if not ok:
            self.error_lbl.configure(text=msg)
            self.reg_btn.configure(state="normal", text="Create Account")
            return

        self.on_go_to_verify({"username": username, "email": email,
                               "password": password, "code": code})

    def _check_username(self, event=None):
        username = self.username.get().strip()
        if len(username) < 3:
            self.error_lbl.configure(text="")
            return
        with db_conn() as conn:
            exists = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        self.error_lbl.configure(text="Username already taken." if exists else "")
