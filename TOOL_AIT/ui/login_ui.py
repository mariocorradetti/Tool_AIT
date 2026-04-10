import ttkbootstrap as tb
from ttkbootstrap.constants import *
import getpass

class LoginUI(tb.Frame):
    def __init__(self, master, app_router):
        super().__init__(master)
        self.app = app_router
        self.pack(fill="both", expand=True)

        # Prende l'username del sistema
        self.username = getpass.getuser()
        
        tb.Label(self, text=f"Welcome {self.username}", font=("Helvetica", 24)).pack(pady=100)
        tb.Button(self, text="Continua", bootstyle="success", command=self.login).pack(pady=20)
    
    def login(self):
        # Aggiorna il footer globale con l'username
        self.app.set_username(self.username)
        # Mostra la schermata di selezione tool
        self.app.show_tool_selection()