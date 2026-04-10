import ttkbootstrap as tb
from ui.login_ui import LoginUI
import os
from PIL import Image, ImageTk

class MainApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")

        self.title("Test Procedure Tool")
        self.geometry("900x650")
        self.resizable(True, True)

        self.username = None  # inizialmente vuoto

        # 🔹 Container principale per le schermate
        self.container = tb.Frame(self)
        self.container.pack(fill="both", expand=True)

        # 🔹 Footer globale
        self.footer = tb.Frame(self, height=40)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)  # mantiene altezza costante

        # 🔹 Logo a destra
        self.add_logo_footer()

        # 🔹 Label username a sinistra
        self.user_label = tb.Label(self.footer, text="", font=("Helvetica", 10))
        self.user_label.pack(side="left", padx=10, pady=5)

        # Avvia login
        self.show_login()

    # 🔹 Cambio schermata generico
    def _show_frame(self, frame_class):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = frame_class(self.container, self)
        frame.pack(fill="both", expand=True)

    def show_login(self):
        self._show_frame(LoginUI)

    def show_tool_selection(self):
        from ui.home_ui import ToolSelectionUI
        self._show_frame(ToolSelectionUI)

    # 🔹 Logo globale a destra
    def add_logo_footer(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "assets", "logo.png")

            img = Image.open(logo_path)
            img.thumbnail((120, 120))

            self.logo_img = ImageTk.PhotoImage(img)
            lbl = tb.Label(self.footer, image=self.logo_img)
            lbl.pack(side="right", padx=10, pady=5)

        except Exception as e:
            print("Errore caricamento logo:", e)

    # 🔹 Imposta username nel footer
    def set_username(self, username):
        self.username = username
        self.user_label.config(text=f"Utente: {username}")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()