import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ui.procedure_ui import ProcedureUI
from ui.data_analysis_ui import DataAnalysisUI
import os
from PIL import Image, ImageTk

class ToolSelectionUI(tb.Frame):
    def __init__(self, master, app_router):
        super().__init__(master)
        self.app = app_router
        self.pack(fill="both", expand=True)

        self.add_logo()

        tb.Label(self, text="Seleziona il Tool", font=("Helvetica", 24)).pack(pady=50)

        tb.Button(self, text="Procedura", bootstyle="primary", width=20,
                  command=self.show_procedure).pack(pady=10)
        tb.Button(self, text="Analisi Dati", bootstyle="success", width=20,
                  command=self.show_analysis).pack(pady=10)

    def add_logo(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "..", "assets", "logo.png")
            img = Image.open(logo_path)
            img.thumbnail((140, 140))
            self.logo_img = ImageTk.PhotoImage(img)
            lbl = tb.Label(self, image=self.logo_img)
            lbl.place(relx=1.0, rely=1.0, anchor="se", x=-15, y=-15)
            lbl.lift()
        except Exception as e:
            print("Errore caricamento logo:", e)

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def show_procedure(self):
        self.clear_screen()
        ProcedureUI(self.master, self.app).pack(fill="both", expand=True)

    def show_analysis(self):
        self.clear_screen()
        DataAnalysisUI(self.master, self.app).pack(fill="both", expand=True)