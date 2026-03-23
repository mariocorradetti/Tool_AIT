import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

class DataAnalyzer:

    def __init__(self):
        self.df = None

    # ==============================
    # CARICA FILE MULTIFORMATO
    # ==============================
    def load_data(self, filepath):
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".xlsx":
            df = pd.read_excel(filepath)

        elif suffix == ".mdf":
            df = self._load_mdf(filepath)

        elif suffix in [".csv", ".txt"]:
            df = self._load_text_file(filepath)

        else:
            raise ValueError(f"Formato file non supportato: {suffix}")

        # Conversione automatica date/numeri
        df = self.try_convert_datetime(df)
        df = self.clean_dataframe(df)

        self.df = df
        return df

    # ==============================
    # LETTURA MDF CON ASAMMDF
    # ==============================
    def _load_mdf(self, filepath):
        try:
            from asammdf import MDF
        except ImportError:
            raise ImportError("Installare il modulo 'asammdf': pip install asammdf")

        mdf = MDF(filepath)
        df = mdf.to_dataframe()  # Carica tutti i canali
        return df

    # ==============================
    # LETTURA CSV/TXT SPORCHI
    # ==============================
    def _load_text_file(self, filepath):
        encodings = ["utf-8", "latin1", "cp1252"]
        seps = ["\t", ";", ","]

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc, errors="ignore") as f:
                    content = f.read()
                # Normalizza separatori multipli in tab
                import re
                content = re.sub(r"[ \t]+", "\t", content)
                from io import StringIO
                buffer = StringIO(content)
                df = pd.read_csv(buffer, sep="\t", engine="python")
                # Se almeno 2 colonne
                if len(df.columns) > 1:
                    df.columns = [col.strip() for col in df.columns]  # pulizia nomi
                    # Converti numeri con virgola
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors='coerce')
                    print(f"Lettura riuscita con encoding '{enc}' e separatore tab normalizzato")
                    return df
            except Exception:
                continue

        raise ValueError("Impossibile leggere il file come CSV/TXT con encodings e separatori comuni.")

    # ==============================
    # PULIZIA DATAFRAME
    # ==============================
    def clean_dataframe(self, df):
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        df_clean = df_numeric.dropna(how='all')
        df_clean.index = range(len(df_clean))
        return df_clean

    # ==============================
    # CONVERSIONE DATE AUTOMATICA
    # ==============================
    def try_convert_datetime(self, df):
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass
        return df

    # ==============================
    # PLOT CON CURSORI
    # ==============================
    def plot_with_cursors(self, df, x_col, y_col, title=None, xlabel=None, ylabel=None):
        y = df[y_col].to_numpy()
        if x_col is None:
            x = np.arange(len(y), dtype=float)
            is_datetime = False
            x_label = xlabel or "Sample"
        else:
            x_raw = df[x_col]
            if np.issubdtype(x_raw.dtype, np.datetime64):
                x = mdates.date2num(x_raw)
                is_datetime = True
            else:
                x = pd.to_numeric(x_raw, errors='coerce').to_numpy(dtype=float)
                is_datetime = False
            x_label = xlabel or x_col

        fig, ax = plt.subplots()
        plt.subplots_adjust(right=0.75)
        ax.plot(x, y)
        ax.set_title(title or f"{y_col} vs {x_label}")
        ax.set_xlabel(x_label)
        ax.set_ylabel(ylabel or y_col)
        ax.grid(True)

        x_min = x[int(len(x) * 0.25)]
        x_max = x[int(len(x) * 0.75)]
        cursor1 = ax.axvline(x=x_min)
        cursor2 = ax.axvline(x=x_max)
        stats_text = fig.text(0.78, 0.5, "", verticalalignment='center')
        selected_cursor = None

        def update_stats():
            xmin = min(cursor1.get_xdata()[0], cursor2.get_xdata()[0])
            xmax = max(cursor1.get_xdata()[0], cursor2.get_xdata()[0])
            mask = (x >= xmin) & (x <= xmax)
            y_sel = y[mask]
            if len(y_sel) > 0:
                mean = np.mean(y_sel)
                rms = np.sqrt(np.mean(y_sel**2))
                ymin = np.min(y_sel)
                ymax = np.max(y_sel)
                if x_col is None or not is_datetime:
                    interval_str = f"{xmin:.3f}\n{xmax:.3f}"
                else:
                    xmin_disp = mdates.num2date(xmin)
                    xmax_disp = mdates.num2date(xmax)
                    interval_str = f"{xmin_disp}\n{xmax_disp}"
                stats_text.set_text(
                    f"Intervallo:\n{interval_str}\n\n"
                    f"Media: {mean:.6f}\n"
                    f"RMS: {rms:.6f}\n"
                    f"Min: {ymin:.6f}\n"
                    f"Max: {ymax:.6f}"
                )
            fig.canvas.draw_idle()

        def on_click(event):
            nonlocal selected_cursor
            if event.inaxes != ax or event.xdata is None:
                return
            dist1 = abs(event.xdata - cursor1.get_xdata()[0])
            dist2 = abs(event.xdata - cursor2.get_xdata()[0])
            selected_cursor = cursor1 if dist1 < dist2 else cursor2

        def on_motion(event):
            if selected_cursor is None or event.inaxes != ax or event.xdata is None:
                return
            selected_cursor.set_xdata([event.xdata])
            update_stats()

        def on_release(event):
            nonlocal selected_cursor
            selected_cursor = None

        fig.canvas.mpl_connect("button_press_event", on_click)
        fig.canvas.mpl_connect("motion_notify_event", on_motion)
        fig.canvas.mpl_connect("button_release_event", on_release)
        update_stats()
        plt.show()