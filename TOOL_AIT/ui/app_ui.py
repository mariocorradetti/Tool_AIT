import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ui.procedure_ui import ProcedureUI
from ui.data_analysis_ui import DataAnalysisUI


class AppUI(tb.Frame):
    def __init__(self, master, username):
        super().__init__(master)

        self.username = username
        self.current_ui = None

        self.pack(fill=BOTH, expand=True)

        # Sidebar
        self.sidebar = tb.Frame(self, width=180)
        self.sidebar.pack(side=LEFT, fill=Y)

        tb.Label(
            self.sidebar,
            text=f"User:\n{self.username}",
            font=("Helvetica", 10)
        ).pack(pady=20)

        tb.Button(
            self.sidebar,
            text="Procedura",
            bootstyle="primary",
            command=self.show_procedure
        ).pack(pady=10, fill=X, padx=10)

        tb.Button(
            self.sidebar,
            text="Analisi Dati",
            bootstyle="success",
            command=self.show_analysis
        ).pack(pady=10, fill=X, padx=10)

        # Area principale
        self.screen_container = tb.Frame(self)
        self.screen_container.pack(side=RIGHT, fill=BOTH, expand=True)

        self.show_procedure()

    def clear_screen(self):
        if self.current_ui:
            self.current_ui.destroy()

    def show_procedure(self):
        self.clear_screen()
        self.current_ui = ProcedureUI(self.screen_container, self)
        self.current_ui.pack(fill=BOTH, expand=True)

    def show_analysis(self):
        self.clear_screen()
        self.current_ui = DataAnalysisUI(self.screen_container, self)
        self.current_ui.pack(fill=BOTH, expand=True)