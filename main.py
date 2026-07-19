import customtkinter as ctk
from database.db import initialize_database
from ui.styles import COLORS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FitTrack")
        self.geometry("1100x720")
        self.minsize(1000, 680)
        self.configure(fg_color=COLORS["bg"])
        self.current_user   = None
        self.current_screen = None
        self._show_login()

    def _show_login(self):
        from ui.login_screen import LoginScreen
        self._switch(LoginScreen(self,
                                  on_login_success=self._on_login,
                                  on_go_to_register=self._show_register))

    def _show_register(self):
        from ui.register_screen import RegisterScreen
        self._switch(RegisterScreen(self,
                                     on_register_success=self._show_login,
                                     on_go_to_login=self._show_login,
                                     on_go_to_verify=self._show_verify))

    def _show_verify(self, pending):
        from ui.verify_email_screen import VerifyEmailScreen
        from auth.auth_manager import AuthManager

        def on_verified():
            ok, msg = AuthManager().register_user(
                pending["username"], pending["email"], pending["password"]
            )
            if ok:
                self._show_login()
            else:
                self._show_verify_error(msg, pending)

        self._switch(VerifyEmailScreen(self,
                                        email=pending["email"],
                                        code=pending["code"],
                                        on_verified=on_verified,
                                        on_back=self._show_register))

    def _show_verify_error(self, msg, pending):
        from ui.verify_email_screen import VerifyEmailScreen
        screen = VerifyEmailScreen(self,
                                    email=pending["email"],
                                    code=pending["code"],
                                    on_verified=lambda: None,
                                    on_back=self._show_register)
        self._switch(screen)
        screen.error_lbl.configure(text=f"Registration failed: {msg}")

    def _on_login(self, user):
        self.current_user = user
        self._show_dashboard()

    def _show_dashboard(self):
        from ui.dashboard_screen import DashboardScreen
        self._switch(DashboardScreen(self,
                                      user=self.current_user,
                                      on_start_workout=self._show_workout,
                                      on_view_history=self._show_history,
                                      on_account_settings=self._show_account,
                                      on_logout=self._logout))

    def _show_workout(self):
        from ui.workout_screen import WorkoutScreen
        self._switch(WorkoutScreen(self, user=self.current_user, on_finish=self._show_dashboard))

    def _show_history(self):
        from ui.history_screen import HistoryScreen
        self._switch(HistoryScreen(self, user=self.current_user, on_back=self._show_dashboard))

    def _show_account(self):
        from ui.account_screen import AccountScreen
        from auth.auth_manager import AuthManager
        # Reload user to pick up latest reminder settings
        fresh_user = AuthManager().get_user_by_id(self.current_user["id"])
        self._switch(AccountScreen(self, user=fresh_user,
                                    on_back=self._show_dashboard,
                                    on_logout=self._logout))

    def _logout(self):
        self.current_user = None
        self._show_login()

    def _switch(self, new_screen):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = new_screen
        new_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    initialize_database()
    app = App()
    app.mainloop()
