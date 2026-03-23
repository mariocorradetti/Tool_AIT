import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import re
from io import StringIO

class DataAnalyzer:
    def __init__(self):
        self.df = None

    def load_data(self, filepath):
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".xlsx":
            df = pd.read_excel(filepath)
        elif suffix == ".mdf":
            try:
                df = self._load_mdf(filepath)
            except Exception as e:
                print(f"File .mdf non binario. Provo lettura testuale... Error: {e}")
                df = self._load_text_file(filepath)
        elif suffix in [".csv", ".txt", ".dat"]:
            df = self._load_text_file(filepath)
        else:
            raise ValueError(f"Formato file non supportato: {suffix}")

        df = self.try_convert_datetime(df)
        self.df = df
        return df

    def _load_mdf(self, filepath):
        try:
            from asammdf import MDF
        except ImportError:
            raise ImportError("Installare 'asammdf': pip install asammdf")
        mdf = MDF(filepath)
        return mdf.to_dataframe(reduce_memory_usage=True)

    def _load_text_file(self, filepath):
        encodings = ["utf-8", "latin1", "cp1252"]
        separators = [";", "\t", ","]

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc, errors="ignore") as f:
                    content = f.read()
                if not content: continue
                lines = [l.strip() for l in content.splitlines() if l.strip()]

                data_start_idx = -1
                detected_sep = ";"

                for i, line in enumerate(lines):
                    for s in separators:
                        parts = line.split(s)
                        numeric_count = 0
                        for p in parts[:4]: 
                            try:
                                val = p.strip().replace(',', '.')
                                if val == "" or val.lower() in ["none", "nan"]: continue
                                float(val); numeric_count += 1
                            except ValueError: continue
                        if numeric_count >= 2:
                            data_start_idx = i
                            detected_sep = s
                            break
                    if data_start_idx != -1: break

                if data_start_idx > 0:
                    header_line = lines[data_start_idx - 1]
                    column_names = [c.strip() for c in header_line.split(detected_sep) if c.strip()]
                    df = pd.read_csv(StringIO("\n".join(lines[data_start_idx:])),
                                     sep=detected_sep, names=column_names, engine='python', decimal=',')
                else:
                    df = pd.read_csv(StringIO("\n".join(lines)), sep=detected_sep, engine='python', decimal=',')

                if not df.empty:
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                    df.columns = [str(c).replace('"', '').replace("'", "").strip() for c in df.columns]
                    for col in df.columns:
                        clean_s = df[col].astype(str).str.replace(',', '.').str.strip()
                        df[col] = pd.to_numeric(clean_s, errors='coerce')
                    df = df.dropna(how='all').reset_index(drop=True)
                    print(f"File caricato! Separatore: '{detected_sep}' (Encoding: {enc})")
                    return df
            except: continue
        raise ValueError("Impossibile interpretare il file.")

    def try_convert_datetime(self, df):
        for col in df.columns:
            if df[col].dtype == object:
                converted = pd.to_datetime(df[col], errors='coerce')
                if converted.notna().sum() > len(df) * 0.8:
                    df[col] = converted
                else:
                    try:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                    except: pass
        return df

    # ============================================================
    # METODO COMPATIBILE CON LA TUA UI (data_analysis_ui.py)
    # ============================================================
    def plot_with_cursors(self, df, x_col, y_col1, y_col2=None, title=None, xlabel=None, ylabel=None):
            y1 = df[y_col1].to_numpy()
            y2 = None
            if y_col2 is not None and str(y_col2) != "None":
                y2 = df[y_col2].to_numpy()

            # Gestione asse X
            if x_col is None or x_col not in df.columns:
                x = np.arange(len(y1), dtype=float)
                is_datetime, x_label_final = False, (xlabel if xlabel else "Sample")
            else:
                x_raw = df[x_col]
                if np.issubdtype(x_raw.dtype, np.datetime64):
                    x, is_datetime = mdates.date2num(x_raw), True
                else:
                    x, is_datetime = pd.to_numeric(x_raw, errors='coerce').to_numpy(dtype=float), False
                x_label_final = xlabel if xlabel else x_col

            # --- MODIFICA QUI: Aumentiamo il margine destro a 0.65 (più spazio vuoto) ---
            fig, ax1 = plt.subplots(figsize=(13, 6))
            plt.subplots_adjust(right=0.65) 

            # Segnale 1 (Sinistra)
            ax1.plot(x, y1, color='tab:blue', label=y_col1, linewidth=1.5)
            ax1.set_xlabel(x_label_final)
            ax1.set_ylabel(ylabel if ylabel else y_col1, color='tab:blue', fontweight='bold')
            ax1.tick_params(axis='y', labelcolor='tab:blue')
            ax1.grid(True, alpha=0.3)

            # Segnale 2 (Destra)
            ax2 = None
            if y2 is not None:
                ax2 = ax1.twinx()
                ax2.plot(x, y2, color='tab:red', label=y_col2, linewidth=1.5, alpha=0.8)
                ax2.set_ylabel(y_col2, color='tab:red', fontweight='bold')
                ax2.tick_params(axis='y', labelcolor='tab:red')

            if is_datetime:
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                fig.autofmt_xdate()

            # Cursori
            c1 = ax1.axvline(x[len(x)//4], color='black', linestyle='--', alpha=0.6)
            c2 = ax1.axvline(x[3*len(x)//4], color='black', linestyle='--', alpha=0.6)

            # --- MODIFICA QUI: Spostiamo il testo a 0.82 (molto più a destra) ---
            stats_text = fig.text(0.82, 0.5, "", verticalalignment='center', family='monospace', fontsize=9)
            selected_cursor = None

            def update_stats():
                xmin, xmax = min(c1.get_xdata()[0], c2.get_xdata()[0]), max(c1.get_xdata()[0], c2.get_xdata()[0])
                mask = (x >= xmin) & (x <= xmax)
                
                txt = "ANALISI INTERVALLO\n"
                txt += f"{'-'*18}\n"
                
                # Stats Y1
                y1_s = y1[mask]
                if len(y1_s) > 0:
                    txt += f"[Y1: {y_col1[:10]}]\nAvg: {np.nanmean(y1_s):.3f}\nMax: {np.nanmax(y1_s):.3f}\nRMS: {np.sqrt(np.nanmean(y1_s**2)):.3f}\n"
                
                # Stats Y2
                if y2 is not None:
                    y2_s = y2[mask]
                    if len(y2_s) > 0:
                        txt += f"\n[Y2: {y_col2[:10]}]\nAvg: {np.nanmean(y2_s):.3f}\nMax: {np.nanmax(y2_s):.3f}\nRMS: {np.sqrt(np.nanmean(y2_s**2)):.3f}\n"

                stats_text.set_text(txt)
                fig.canvas.draw_idle()

            # Eventi mouse
            # --- FUNZIONI EVENTI CORRETTE ---
            def on_click(event):
                nonlocal selected_cursor
                if event.inaxes not in [ax1, ax2] or event.xdata is None: 
                    return
                
                # Calcola quale cursore è più vicino al click
                d1 = abs(event.xdata - c1.get_xdata()[0])
                d2 = abs(event.xdata - c2.get_xdata()[0])
                
                # Soglia di aggancio: il click deve essere vicino al cursore
                if min(d1, d2) < (ax1.get_xlim()[1] - ax1.get_xlim()[0]) * 0.05:
                    selected_cursor = c1 if d1 < d2 else c2

            def on_motion(event):
                nonlocal selected_cursor
                if selected_cursor is not None and event.xdata is not None:
                    selected_cursor.set_xdata([event.xdata])
                    update_stats()

            def on_release(event):
                nonlocal selected_cursor
                selected_cursor = None  # <--- Fondamentale: rilascia il cursore

            # Connessione eventi
            fig.canvas.mpl_connect("button_press_event", on_click)
            fig.canvas.mpl_connect("motion_notify_event", on_motion)
            fig.canvas.mpl_connect("button_release_event", on_release)
            
            update_stats()
            plt.show()