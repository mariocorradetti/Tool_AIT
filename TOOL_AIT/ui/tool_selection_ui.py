# ui/tool_selection_ui.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class ToolSelectionUI(tb.Frame):
    def __init__(self, master, app_router):
        super().__init__(master)
        self.app = app_router
        self.pack(fill="both", expand=True)

        frame = tb.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(frame, text="Seleziona il Tool da utilizzare", font=("Helvetica", 18)).pack(pady=20)

        tb.Button(frame, text="Procedura", bootstyle="primary", width=20,
                  command=self.app.show_procedure_tool).pack(pady=10)

        tb.Button(frame, text="Analisi Dati", bootstyle="success", width=20,
                  command=self.app.show_data_analysis_tool).pack(pady=10)