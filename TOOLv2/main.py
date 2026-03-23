import ttkbootstrap as tb
from ui.login_ui import LoginUI

class MainApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Test Procedure Tool")
        self.geometry("900x650")
        self.resizable(True, True)

        # Container principale per cambiare le schermate
        self.container = tb.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Avvia la schermata di login
        self.show_login()

    # ==============================
    # Mostra la schermata di login
    # ==============================
    def show_login(self):
        # Distrugge eventuali widget precedenti
        for widget in self.container.winfo_children():
            widget.destroy()
        # Mostra login UI
        LoginUI(self.container, self).pack(fill="both", expand=True)

    # ==============================
    # Mostra la schermata di selezione tool
    # ==============================
    def show_tool_selection(self):
        from ui.home_ui import ToolSelectionUI
        # Pulisce container
        for widget in self.container.winfo_children():
            widget.destroy()
        # Mostra selezione tool
        ToolSelectionUI(self.container, self).pack(fill="both", expand=True)


# ==============================
# Avvio applicazione
# ==============================
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()