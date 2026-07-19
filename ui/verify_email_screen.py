import customtkinter as ctk
from ui.styles import *


class VerifyEmailScreen(ctk.CTkFrame):
    def __init__(self, master, email, code, on_verified, on_back):
        super().__init__(master, fg_color=COLORS["bg"])
        self.email       = email
        self.code        = code
        self.on_verified = on_verified
        self.on_back     = on_back
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.configure(width=420, height=480)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text="💪 FitTrack",
                     font=FONT_TITLE, text_color=COLORS["accent"]).pack(pady=(40, 4))
        ctk.CTkLabel(card, text="Check your email",
                     font=FONT_H2, text_color=COLORS["text"]).pack(pady=(0, 8))
        ctk.CTkLabel(card, text=f"We sent a 6-digit code to:\n{self.email}",
                     font=FONT_BODY, text_color=COLORS["text_sub"],
                     justify="center").pack(pady=(0, 24))

        self.code_entry = ctk.CTkEntry(
            card, placeholder_text="Enter 6-digit code",
            width=320, height=54, font=("Segoe UI", 22, "bold"), justify="center"
        )
        self.code_entry.pack(pady=6)
        self.code_entry.bind("<Return>", lambda e: self._verify())

        self.error_lbl = ctk.CTkLabel(card, text="",
                                       font=FONT_SMALL, text_color=COLORS["error"])
        self.error_lbl.pack(pady=(4, 0))

        self.verify_btn = ctk.CTkButton(
            card, text="Verify Email", width=320, height=44, font=FONT_H3,
            command=self._verify,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000"
        )
        self.verify_btn.pack(pady=(12, 6))

        ctk.CTkButton(
            card, text="← Back to Register", width=320, height=44, font=FONT_BODY,
            command=self.on_back,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"], text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        ).pack(pady=6)

    def _verify(self):
        entered = self.code_entry.get().strip().replace(" ", "")
        if not entered:
            self.error_lbl.configure(text="Please enter the code.")
            return
        if entered == self.code:
            self.on_verified()
        else:
            self.error_lbl.configure(text="Incorrect code. Please try again.")
            self.code_entry.delete(0, "end")
