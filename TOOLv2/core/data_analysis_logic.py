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
                    # Prova prima come vero MDF binario
                    df = self._load_mdf(filepath)
                except Exception as e:
                    # Se fallisce perché è un "finto" MDF (testuale), usa il lettore CSV
                    print(f"Il file .mdf non è binario standard. Provo lettura testuale... Error: {e}")
                    df = self._load_text_file(filepath)

            elif suffix in [".csv", ".txt", ".dat"]:
                df = self._load_text_file(filepath)

            else:
                raise ValueError(f"Formato file non supportato: {suffix}")

            # Conversione automatica date/numeri
            df = self.try_convert_datetime(df)
            self.df = df
            return df

    def _load_mdf(self, filepath):
        try:
            from asammdf import MDF
        except ImportError:
            raise ImportError("Installare 'asammdf': pip install asammdf")
        
        mdf = MDF(filepath)
        # Importante: usiamo 'as_matrix=False' e uniamo i canali
        # Se il file è grande, mdf.to_dataframe() senza argomenti può fallire
        df = mdf.to_dataframe(reduce_memory_usage=True)
        return df
    

    def _load_text_file(self, filepath):
            import io
            import re
            
            encodings = ["utf-8", "latin1", "cp1252"]
            # ORDINE DI PRIORITÀ: punto e virgola per primi, poi tab per i tuoi mdf
            separators = [";", "\t", ","]

            for enc in encodings:
                try:
                    with open(filepath, "r", encoding=enc, errors="ignore") as f:
                        content = f.read()
                    
                    if not content: continue
                    # Pulizia righe: rimuoviamo spazi vuoti in testa e coda
                    lines = [l.strip() for l in content.splitlines() if l.strip()]

                    # 1. IDENTIFICAZIONE SEPARATORE E RIGA DATI
                    data_start_idx = -1
                    detected_sep = ";" # Default iniziale

                    for i, line in enumerate(lines):
                        # Proviamo i separatori nell'ordine definito sopra
                        for s in separators:
                            parts = line.split(s)
                            numeric_count = 0
                            # Controlliamo i primi 4 elementi della riga per vedere se sono numeri
                            for p in parts[:4]: 
                                try:
                                    # Pulizia per test numerico: togliamo spazi e cambiamo virgola in punto
                                    val = p.strip().replace(',', '.')
                                    if val == "" or val.lower() == "none" or val.lower() == "nan": 
                                        continue
                                    float(val)
                                    numeric_count += 1
                                except ValueError:
                                    continue
                            
                            # Se troviamo almeno 2 numeri, abbiamo trovato l'inizio dei dati!
                            if numeric_count >= 2:
                                data_start_idx = i
                                detected_sep = s
                                break
                        if data_start_idx != -1:
                            break

                    # 2. ESTRAZIONE NOMI COLONNE E CARICAMENTO
                    if data_start_idx > 0:
                        # La testata è ESATTAMENTE la riga sopra i primi numeri trovati
                        header_line = lines[data_start_idx - 1]
                        # Estraiamo i nomi usando il separatore rilevato
                        column_names = [c.strip() for c in header_line.split(detected_sep) if c.strip()]
                        
                        # Carichiamo i dati effettivi
                        data_buffer = io.StringIO("\n".join(lines[data_start_idx:]))
                        df = pd.read_csv(
                            data_buffer,
                            sep=detected_sep,
                            names=column_names,
                            engine='python',
                            decimal=',',
                            on_bad_lines='skip'
                        )
                    else:
                        # Fallback standard (es. file con solo nomi e numeri subito sotto)
                        df = pd.read_csv(
                            io.StringIO("\n".join(lines)),
                            sep=detected_sep,
                            engine='python',
                            decimal=',',
                            on_bad_lines='skip'
                        )

                    # 3. PULIZIA E CONVERSIONE FINALE
                    if not df.empty:
                        # Rimuoviamo colonne "Unnamed" generate da separatori extra a fine riga
                        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                        
                        # Puliamo i nomi delle colonne da eventuali virgolette
                        df.columns = [str(c).replace('"', '').replace("'", "").strip() for c in df.columns]
                        
                        for col in df.columns:
                            # Forza la conversione numerica gestendo virgole e spazi
                            clean_series = df[col].astype(str).str.replace(',', '.').str.strip()
                            df[col] = pd.to_numeric(clean_series, errors='coerce')
                        
                        # Elimina righe totalmente vuote
                        df = df.dropna(how='all').reset_index(drop=True)
                        
                        print(f"File caricato! Separatore: '{detected_sep}' (Encoding: {enc})")
                        return df

                except Exception as e:
                    print(f"Tentativo {enc} fallito: {e}")
                    continue

            raise ValueError("Impossibile interpretare il file. Controlla il formato o i separatori.")

    def try_convert_datetime(self, df):
        for col in df.columns:
            # Se la colonna sembra una stringa/oggetto
            if df[col].dtype == object:
                # Prova a convertire in data
                converted = pd.to_datetime(df[col], errors='coerce')
                # Se almeno l'80% dei valori è diventato data, tieni la conversione
                if converted.notna().sum() > len(df) * 0.8:
                    df[col] = converted
                else:
                    # Altrimenti prova a pulire i numeri (es. virgole europee)
                    try:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                    except:
                        pass
        return df

    def plot_with_cursors(self, df, x_col, y_col, title=None, xlabel=None, ylabel=None):
        # ... (Il tuo codice dei cursori rimane valido, assicurati solo che x_col esista)
        if x_col not in df.columns and x_col is not None:
             print(f"Attenzione: {x_col} non trovato. Uso indice.")
             x_col = None
        
        # --- (Il resto della tua funzione plot_with_cursors è corretta) ---
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

        # Gestione asse X se data
        if is_datetime:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            fig.autofmt_xdate()

        cursor1 = ax.axvline(x=x[len(x)//4], color='r')
        cursor2 = ax.axvline(x=x[3*len(x)//4], color='g')
        stats_text = fig.text(0.78, 0.5, "", verticalalignment='center', family='monospace')
        selected_cursor = None

        def update_stats():
            xmin = min(cursor1.get_xdata()[0], cursor2.get_xdata()[0])
            xmax = max(cursor1.get_xdata()[0], cursor2.get_xdata()[0])
            mask = (x >= xmin) & (x <= xmax)
            y_sel = y[mask]
            
            if len(y_sel) > 0:
                mean_val = np.nanmean(y_sel)
                rms_val = np.sqrt(np.nanmean(y_sel**2))
                ymin_val = np.nanmin(y_sel)
                ymax_val = np.nanmax(y_sel)
                
                if not is_datetime:
                    interval_str = f"Inizio: {xmin:.2f}\nFine:   {xmax:.2f}"
                else:
                    interval_str = f"Inizio: {mdates.num2date(xmin).strftime('%H:%M:%S')}\nFine:   {mdates.num2date(xmax).strftime('%H:%M:%S')}"
                
                stats_text.set_text(
                    f"INTERVALLO:\n{interval_str}\n\n"
                    f"Media: {mean_val:.4f}\n"
                    f"RMS:   {rms_val:.4f}\n"
                    f"Min:   {ymin_val:.4f}\n"
                    f"Max:   {ymax_val:.4f}"
                )
            fig.canvas.draw_idle()

        def on_click(event):
            nonlocal selected_cursor
            if event.inaxes != ax or event.xdata is None: return
            dist1 = abs(event.xdata - cursor1.get_xdata()[0])
            dist2 = abs(event.xdata - cursor2.get_xdata()[0])
            selected_cursor = cursor1 if dist1 < dist2 else cursor2

        def on_motion(event):
            if selected_cursor is None or event.inaxes != ax or event.xdata is None: return
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