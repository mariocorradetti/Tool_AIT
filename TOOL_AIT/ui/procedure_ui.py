from tkinter import filedialog, Toplevel, LEFT, BOTH, Y, CENTER
import tkinter as tk
import tkinter.ttk as ttk
import getpass
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from core.excel_manager import ExcelManager
from core.procedure_logic import ProcedureLogic

class ProcedureUI(tb.Frame):
    def __init__(self, master, app_router):
        super().__init__(master)
        self.app = app_router
        self.pack(fill=BOTH, expand=True)

        # ---------------- TOP FRAME: Pulsante Back ----------------
        self.top_frame = tb.Frame(self)
        self.top_frame.pack(fill="x", side="top")
        self.back_button = tb.Button(
            self.top_frame,
            text="Back",
            bootstyle="secondary",
            command=self.app.show_tool_selection
        )
        self.back_button.pack(anchor="nw", padx=10, pady=10)

        # ---------------- VARIABILI ----------------
        self.excel_manager = ExcelManager()
        self.logic = None
        self.username = getpass.getuser()

        # Mostra schermata selezione file
        self.build_file_screen()

    # ---------- FILE SELECTION ----------
    def build_file_screen(self):
        # Distruggi solo widget sotto top_frame
        for w in self.winfo_children():
            if w is not self.top_frame:
                w.destroy()

        frame = tb.Frame(self)
        frame.pack(expand=True)
        tb.Label(frame, text="Seleziona file Excel per procedura", font=("Helvetica", 18)).pack(pady=30)
        tb.Button(frame, text="Seleziona file", bootstyle="primary",
                  command=self.open_excel).pack(pady=20)

    def open_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        self.excel_manager.load(path)
        self.logic = ProcedureLogic(self.excel_manager)
        self.build_main_ui()

    # ---------- MAIN UI ----------
    def build_main_ui(self):
        # Distruggi solo widget sotto top_frame
        for w in self.winfo_children():
            if w is not self.top_frame:
                w.destroy()

        # --- Notebook con tabs ---
        notebook = tb.Notebook(self)
        notebook.pack(fill=BOTH, expand=True)

        self.main_tab = tb.Frame(notebook)
        self.steps_tab = tb.Frame(notebook)

        notebook.add(self.main_tab, text="Current Step")
        notebook.add(self.steps_tab, text="All Steps")

        # ================= CURRENT STEP TAB =================
        self.step_label = tb.Label(self.main_tab, font=("Helvetica", 16))
        self.step_label.pack(pady=10)

        self.desc_label = tb.Label(self.main_tab, wraplength=700, justify=CENTER)
        self.desc_label.pack(pady=5)

        self.expected_label = tb.Label(self.main_tab)
        self.expected_label.pack(pady=5)

        tb.Label(self.main_tab, text="Measured value").pack()
        self.measured_entry = tb.Entry(self.main_tab)
        self.measured_entry.pack(pady=5)

        tb.Label(self.main_tab, text="Nuovo Remark").pack()
        self.remarks_entry = tb.Text(self.main_tab, height=4, width=60)
        self.remarks_entry.pack(pady=5)

        self.old_remarks_label = tb.Label(self.main_tab, text="", foreground="gray")
        self.old_remarks_label.pack(pady=5)

        button_frame = tb.Frame(self.main_tab)
        button_frame.pack(pady=20)

        tb.Button(button_frame, text="Previous", bootstyle="secondary",
                  command=self.previous_step).pack(side=LEFT, padx=10)
        tb.Button(button_frame, text="Next", bootstyle="success",
                  command=self.next_step).pack(side=LEFT, padx=10)
        
        # Bottone firma (inizialmente nascosto)
        self.sign_button = tb.Button(
            self.main_tab,
            text="Firma per passare allo step successivo",
            bootstyle="warning",
            command=self.confirm_signature
        )
        self.sign_button.pack(pady=10)
        self.sign_button.pack_forget()

        # Stato
        self.waiting_for_signature = False

        # ================= ALL STEPS TAB =================
        container = tb.Frame(self.steps_tab)
        container.pack(fill=BOTH, expand=True)

        canvas = tk.Canvas(container)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        self.steps_frame = tb.Frame(canvas)
        self.steps_window_id = canvas.create_window((0, 0), window=self.steps_frame, anchor="nw")

        # Aggiorna dimensioni del frame interno
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self.steps_window_id, width=event.width)

        self.steps_frame.bind("<Configure>", on_frame_configure)

        # Treeview con numero step e descrizione
        self.steps_table = ttk.Treeview(
            self.steps_frame,
            columns=("Step", "Description"),
            show="headings",
            height=20
        )
        self.steps_table.heading("Step", text="Step")
        self.steps_table.heading("Description", text="Description")
        self.steps_table.column("Step", width=80, anchor="center")
        self.steps_table.column("Description", width=700)
        self.steps_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Doppio click per aprire finestra step
        self.steps_table.bind("<Double-1>", self.open_step_window)

        self.populate_steps_table()
        self.show_step()

    # ---------- POPULATE TREE ----------
    def populate_steps_table(self):
        for row in self.steps_table.get_children():
            self.steps_table.delete(row)

        i = 2
        while True:
            step = self.excel_manager.get_step(i)
            if step is None:
                break
            self.steps_table.insert("", "end", iid=i, values=(step["number"], step["description"]))
            i += 1

    # ---------- OPEN STEP WINDOW ----------
    def open_step_window(self, event):
        selected = self.steps_table.focus()
        if not selected:
            return

        row_index = int(selected)
        step = self.excel_manager.get_step(row_index)
        if step is None:
            return

        win = Toplevel(self)
        win.title(f"Step {step['number']}")
        win.geometry("700x400")

        tb.Label(win, text=f"Step {step['number']}", font=("Helvetica", 16, "bold")).pack(pady=10)
        tb.Label(win, text=step["description"], wraplength=650, justify=CENTER).pack(pady=10)
        tb.Label(win, text=f"Expected: {step['expected']}").pack(pady=5)
        tb.Label(win, text=f"Remarks: {step['remarks'] or 'None'}", foreground="gray").pack(pady=10)

    # ---------- NAVIGATION ----------
    def show_step(self):
        step = self.excel_manager.get_step(self.logic.current_row)

        # ===== PROCEDURA COMPLETATA =====
        if step is None:
            self.step_label.config(text="✔ Procedura completata")
            self.desc_label.config(text="")
            self.expected_label.config(text="")

            # Nasconde campi input
            self.measured_entry.pack_forget()
            self.remarks_entry.pack_forget()
            self.old_remarks_label.pack_forget()

            return

        # ===== STEP NORMALE =====
        self.step_label.config(text=f"Step {step['number']}")
        self.desc_label.config(text=step['description'])
        self.expected_label.config(text=f"Expected: {step['expected']}")

        # Ri-mostra i campi se erano nascosti
        if not self.measured_entry.winfo_ismapped():
            self.measured_entry.pack(pady=5)

        if not self.remarks_entry.winfo_ismapped():
            self.remarks_entry.pack(pady=5)

        if not self.old_remarks_label.winfo_ismapped():
            self.old_remarks_label.pack(pady=5)

        self.measured_entry.delete(0, "end")
        self.measured_entry.insert(0, step['measured'] or "")

        self.remarks_entry.delete("1.0", "end")
        self.old_remarks_label.config(text=f"Remark precedente: {step['remarks'] or ''}")

    def next_step(self):
        if self.waiting_for_signature:
            return

        # Mostra bottone firma
        self.sign_button.pack(pady=10)
        self.waiting_for_signature = True

    def confirm_signature(self):
        measured = self.measured_entry.get()
        remark = self.remarks_entry.get("1.0", "end-1c").strip()

        # Firma (salvataggio)
        self.excel_manager.sign_step(
            self.logic.current_row,
            self.username,
            measured,
            remark
        )

        # Reset stato
        self.waiting_for_signature = False
        self.sign_button.pack_forget()

        # Vai allo step successivo
        self.logic.next_step()
        self.show_step()

    def previous_step(self):
        self.logic.previous_step()
        self.show_step()