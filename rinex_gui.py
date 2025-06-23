#!/usr/bin/env python3

import sys
import zipfile
import tkinter as tk
import json

from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from termcolor import colored

from rinex_fixer import RinexFixer
from rinex_filename_fixer import rinex_filename_fixer
from logger import Observer, logger

CONFIG_FILE = Path(__file__).with_suffix('.config')


class GUILogObserver(Observer):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def log(self, message):
        self.text_widget.insert('end', message + "\n")
        self.text_widget.see('end')


class CLIDebugObserver(Observer):
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode

    def log(self, message):
        if (self.debug_mode):
            print(f"[LOG] {message}")

    def debug(self, message):
        if (self.debug_mode):
            print(f"{colored('[DEBUG]: ','yellow')}{message}")

    def error(self, message):
        print(f"{colored('[ERRO]: ','red')}{message}")


class RinexGUI:
    def __init__(self, debug_mode, root):
        self.root = root
        self.root.configure(background='white')
        self.root.title("RINEX GPS Week Rollover Fixer")
        self.root.geometry("600x400")
        self.root.resizable(False, False)  # Prevents window resizing

        self.config_station_id = "SSTR"
        self._load_config()

        self.style = ttk.Style()
        self.style.configure('TLabel', font=(
            'Segoe UI', 10), background='white')
        self.style.configure('TButton', font=(
            'Segoe UI', 10), padding=3, relief=tk.FLAT, background="#f0f0f0")
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TFrame', padding=10, background='white')

        self.fixer = RinexFixer()

        logger.add_observer(CLIDebugObserver(debug_mode))

        self.selected_file = tk.StringVar()
        self.station_id_var = tk.StringVar(
            value=self.config_station_id)

        main_frame = ttk.Frame(root, style='TFrame')
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(2, weight=4)
        main_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(
            main_frame,
            text="Arquivo RINEX:",
            style='TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=10)

        self.file_entry = ttk.Entry(
            main_frame,
            textvariable=self.selected_file,
            width=40,
            style='TEntry'
        )
        self.file_entry.grid(row=0, column=1, columnspan=2,
                             padx=5, pady=2, sticky=tk.EW)

        ttk.Button(
            main_frame,
            text="Procurar",
            command=self.browse_file,
            style='TButton',
            width=15,
        ).grid(row=0, column=3, pady=2, sticky=tk.E)

        self.result_log = tk.Text(
            main_frame,
            height=13,
            font=('Segoe UI', 10),
            background='white'
        )
        self.result_log.grid(row=1, column=0, columnspan=4,
                             pady=5,  sticky="nsew")

        logger.add_observer(GUILogObserver(self.result_log))

        ttk.Label(
            main_frame,
            text="Station ID:",
            style='TLabel'
        ).grid(row=2, column=0, pady=5, sticky=tk.W)

        self.station_id_entry = ttk.Entry(
            main_frame,
            textvariable=self.station_id_var,
            width=8,
            style='TEntry',
            justify='center'
        )
        self.station_id_entry.grid(
            row=2, column=1, sticky=tk.EW, padx=2)

        self.fix_button = ttk.Button(
            main_frame,
            text="Corrigir",
            command=self.fix_file,
            state='disabled',
            style='TButton'
        )
        self.fix_button.grid(row=3, column=0, padx=2, pady=15, sticky=tk.W)

        self.zip_button = ttk.Button(
            main_frame,
            text="Comprimir arquivos",
            command=self.zip_rinex_files,
            state='disabled',
            style='TButton'
        )
        self.zip_button.grid(row=3, column=2, padx=2, pady=15, sticky=tk.EW)

        # Botão Sair
        self.exit_button = ttk.Button(
            main_frame,
            text="Sair",
            command=self._on_close,
            style='TButton'
        )
        self.exit_button.grid(row=3, column=3, padx=2, pady=15, sticky=tk.E)

        root.protocol("WM_DELETE_WINDOW", self._on_close)  # <-- Adicionado

        root.update_idletasks()

    def browse_file(self):
        filetypes = (
            ('Arquivos de observação RINEX', '*.??O'),
            ('Todos os arquivos', '*.*')
        )

        filename = filedialog.askopenfilename(
            title='Selecione um arquivo RINEX',
            initialdir='./arquivos',
            filetypes=filetypes
        )

        if filename:
            file_path_obj = Path(filename)
            self.selected_file.set(str(file_path_obj))
            # self.file_name =
            self.fix_button['state'] = 'enabled'
            self.zip_button['state'] = 'enabled'
            self.result_log.delete(1.0, tk.END)
            logger.notify(
                f"Arquivo aberto: {file_path_obj.name}", tk.END)
            logger.notify(
                "Pronto para correção. Clique no botão 'Corrigir' para iniciar.", tk.END)

    def fix_file(self):
        file_path = self.selected_file.get()
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo para corrigir")
            return

        try:
            logger.notify("\nIniciando processo de correção...\n", tk.END)
            logger.debug(f"Running rinex_filename_fixer() on {file_path}")

            # Pega o station_id da caixa de texto
            station_id = self.station_id_var.get().strip() or "SSTR"

            fixed_filename = rinex_filename_fixer(
                file_path, station_id_override=station_id)

            if (not fixed_filename):
                return

            file_path_obj = Path(file_path)

            dir_path = file_path_obj.parent
            rinex_pattern = f"{fixed_filename}.[0-9][0-9]O"
            rinex_observation_files = list(dir_path.glob(rinex_pattern))
            if not rinex_observation_files:
                logger.notify("Arquivo de observação não encontrado")
                return
            rinex_observation_file = str(rinex_observation_files[0])

            self.selected_file.set(rinex_observation_file)

            success = self.fixer.process_rinex_file(rinex_observation_file)

            if success:
                logger.notify("\n")
                logger.notify("Correção concluída com sucesso!")
                # messagebox.showinfo(
                #     "Sucesso", "Arquivo corrigido com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao corrigir o arquivo")
        except Exception as e:
            logger.error(e)
            messagebox.showerror("Erro", f"Erro ao corrigir arquivo: {str(e)}")

    def zip_rinex_files(self):
        file_path = self.selected_file.get()
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo para comprimir")
            return

        try:
            file_path_obj = Path(file_path)
            file_dir = file_path_obj.parent
            base_name = file_path_obj.stem
            pattern = f"{base_name}.[0-9][0-9][G,N,O]"
            rinex_files = list(file_dir.glob(pattern))
            if not rinex_files:
                messagebox.showerror(
                    "Erro", "Nenhum arquivo RINEX encontrado para compressão")
                return

            zip_filename = file_dir / f"{base_name}_RINEX.zip"
            with zipfile.ZipFile(str(zip_filename), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in rinex_files:
                    zipf.write(str(file), file.name)
            logger.notify(
                f"\nArquivos comprimidos com sucesso em: {zip_filename}\n", tk.END)
            logger.notify("Arquivos incluídos:\n", tk.END)
            for file in rinex_files:
                logger.notify(f"- {file.name}\n", tk.END)
            messagebox.showinfo("Sucesso", "Arquivos comprimidos com sucesso!")
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao comprimir arquivos: {str(e)}")

    def _load_config(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    pos = config['pos']
                    geom = f"{pos['width']}x{pos['height']}+{pos['x']}+{pos['y']}"
                    self.root.geometry(geom)

                    self.config_station_id = config['station_id']
        except Exception:
            pass

    def _save_config(self):
        try:
            geom = self.root.geometry()
            size, x, y = geom.split('+')
            width, height = size.split('x')
            config = {
                "pos": {
                    "width": int(width),
                    "height": int(height),
                    "x": int(x),
                    "y": int(y)
                },
                "station_id": self.station_id_var.get()
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception:
            pass
            pass

    def _on_close(self):
        self._save_config()
        self.root.destroy()


def main():
    root = tk.Tk()
    debug_mode = any(arg in ("--debug", "-D") for arg in sys.argv)
    RinexGUI(debug_mode, root)
    root.mainloop()


if __name__ == "__main__":
    main()
