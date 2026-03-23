import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, END, DISABLED, NORMAL, Text
from core.data_analysis_logic import DataAnalyzer

class DataAnalysisUI(tb.Frame):
    def __init__(self, master, app_router):
        super().__init__(master)
        self.app = app_router
        self.pack(fill=BOTH, expand=True)

        self.analyzer = DataAnalyzer()
        self.df = None

        # Titolo pagina
        tb.Label(self, text="Analisi Dati", font=("Helvetica", 20)).pack(pady=20)

        # Bottone per selezionare file
        tb.Button(self, text="Seleziona file", bootstyle="primary", command=self.load_file).pack(pady=10)

        # Frame principale per colonne / labels
        self.frame_controls = tb.Frame(self)
        self.frame_controls.pack(pady=10)

        # Bottone Back
        tb.Button(self, text="Back", bootstyle="secondary", command=self.app.show_tool_selection).pack(pady=10)

        # =======================
        # CASSETTA REMARK IN BASSO
        # =======================
        remark_text = (
            "Copley (selezionare csv): è possibile mettere Time come asse X, ma preferibile Samples\n"
            "National Instruments (selezionare csv): selezionare samples come asse X \n"
            "MAGTROL TS grande: plottare su asse X i samples e Y la Torque 1\n"
            "MAGTROL TS piccolo: plottare su asse X i samples e Y la seconda opzione mostrata (Torque Nm)"
        )

        self.remark_box = Text(self, height=5, wrap="word", font=("Helvetica", 11), bg="#d9edf7", fg="black")
        self.remark_box.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        self.remark_box.insert(END, remark_text)
        self.remark_box.configure(state=DISABLED)  # readonly

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        self.df = self.analyzer.load_data(path)
        self.show_column_selectors()

    def show_column_selectors(self):
        # Pulisce frame dei controlli
        for widget in self.frame_controls.winfo_children():
            widget.destroy()

        cols = list(self.df.columns)

        # Selezione Y1 (Principale - Blu)
        tb.Label(self.frame_controls, text="Colonna Y1 (Blu)").grid(row=0, column=0, sticky=W, pady=5)
        self.y_combo = tb.Combobox(self.frame_controls, values=cols, width=30)
        self.y_combo.grid(row=0, column=1, pady=5)

        # Selezione Y2 (Secondaria - Rosso) - OPZIONALE
        tb.Label(self.frame_controls, text="Colonna Y2 (Rosso)").grid(row=1, column=0, sticky=W, pady=5)
        self.y2_combo = tb.Combobox(self.frame_controls, values=["None"] + cols, width=30)
        self.y2_combo.current(0) # Default su None
        self.y2_combo.grid(row=1, column=1, pady=5)

        # Selezione X
        tb.Label(self.frame_controls, text="Colonna X").grid(row=2, column=0, sticky=W, pady=5)
        self.x_combo = tb.Combobox(self.frame_controls, values=["Sample"] + cols, width=30)
        self.x_combo.grid(row=2, column=1, pady=5)

        # Campi Entry (Titolo, Label)
        tb.Label(self.frame_controls, text="Titolo grafico").grid(row=3, column=0, sticky=W, pady=5)
        self.title_entry = tb.Entry(self.frame_controls, width=32)
        self.title_entry.grid(row=3, column=1, pady=5)

        tb.Label(self.frame_controls, text="Asse X").grid(row=4, column=0, sticky=W, pady=5)
        self.xlabel_entry = tb.Entry(self.frame_controls, width=32)
        self.xlabel_entry.grid(row=4, column=1, pady=5)

        tb.Label(self.frame_controls, text="Asse Y1").grid(row=5, column=0, sticky=W, pady=5)
        self.ylabel_entry = tb.Entry(self.frame_controls, width=32)
        self.ylabel_entry.grid(row=5, column=1, pady=5)

        # Bottone Plot
        tb.Button(self.frame_controls, text="Genera Grafico", bootstyle="success", command=self.plot_data).grid(
            row=6, column=0, columnspan=2, pady=15
        )

    def plot_data(self):
        y_col = self.y_combo.get()
        y2_col = self.y2_combo.get()
        x_col = self.x_combo.get()
        
        # Gestione asse X
        if x_col == "Sample":
            x_col = None
        
        # Gestione asse Y2: se è "None" o vuoto, passiamo None reale
        if y2_col == "None" or not y2_col.strip():
            y2_col_to_send = None
        else:
            y2_col_to_send = y2_col

        # Legge valori dai campi entry
        title = self.title_entry.get().strip()
        xlabel = self.xlabel_entry.get().strip()
        ylabel = self.ylabel_entry.get().strip()

        # Valori di default se entry vuote
        title = title if title else f"{y_col} vs {x_col or 'Sample'}"
        xlabel = xlabel if xlabel else (x_col or "Sample")
        ylabel = ylabel if ylabel else y_col

        # Chiamata alla logica
        self.analyzer.plot_with_cursors(
            self.df,
            x_col,
            y_col,
            y_col2=y2_col_to_send,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel
        )