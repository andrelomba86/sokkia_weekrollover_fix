#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from rinex_gpsweek import calculate_gpsw_correction
from rinex_fixer import RinexFixer
from pathlib import Path
import zipfile
import glob


class RinexGUI:
    def __init__(self, root):
        self.root = root
        self.root.configure(background='white')
        self.root.title("RINEX GPS Week Rollover Fixer")
        # self.root.geometry("600x400")
        self.root.resizable(False, False)  # Impede redimensionamento da janela

        # Estilo para os widgets
        self.style = ttk.Style()
        self.style.configure('TLabel', font=(
            'Segoe UI', 10), background='white')
        self.style.configure('TButton', font=(
            'Segoe UI', 10), padding=3, relief=tk.FLAT, background="#f0f0f0")
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TFrame', padding=10, background='white')

        self.fixer = RinexFixer()

        self.selected_file = tk.StringVar()

        main_frame = ttk.Frame(root, style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Arquivo RINEX:", style='TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=10, padx=20)  # Added padx

        self.file_entry = ttk.Entry(
            main_frame, textvariable=self.selected_file, width=40, style='TEntry')
        self.file_entry.grid(row=0, column=1, padx=5,
                             pady=2)  # Reduced padding

        ttk.Button(main_frame, text="Procurar", command=self.browse_file,
                   style='TButton', width=15).grid(row=0, column=2, pady=2, padx=10)

        self.result_text = tk.Text(main_frame, height=15, width=75, font=(
            'Segoe UI', 10), background='white')  # Reduced font size
        self.result_text.grid(row=1, column=0, columnspan=3,
                              pady=5, padx=2)  # Reduced padding

        # Adiciona botão para compressão
        self.zip_button = ttk.Button(main_frame, text="Comprimir Arquivos",
                                     command=self.zip_rinex_files, state='disabled', style='TButton')
        self.zip_button.grid(row=2, column=2, pady=15, padx=2)

        # Move o botão corrigir para a esquerda
        self.fix_button = ttk.Button(
            main_frame, text="Corrigir", command=self.fix_file, state='disabled', style='TButton')
        self.fix_button.grid(row=2, column=0, pady=15,
                             padx=2)  # Reduced padding

        root.update_idletasks()
        root.geometry(root.geometry())

    def browse_file(self):
        filetypes = (
            ('Arquivos RINEX', '*.??O'),
            ('Todos os arquivos', '*.*')
        )

        filename = filedialog.askopenfilename(
            title='Selecione um arquivo RINEX',
            initialdir='./arquivos',
            filetypes=filetypes
        )

        if filename:
            self.selected_file.set(filename)
            self.fix_button['state'] = 'enabled'
            self.zip_button['state'] = 'enabled'
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, f"Arquivo aberto: {os.path.basename(filename)}\n")
            self.result_text.insert(
                tk.END, "Pronto para correção. Clique no botão 'Corrigir' para iniciar.\n")

    def fix_file(self):
        file_path = self.selected_file.get()
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo para corrigir")
            return

        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, "Iniciando processo de correção...\n")

            file_path_obj = Path(file_path)
            success = self.fixer.process_rinex_file(
                file_path_obj, self.result_text)

            if success:
                self.result_text.insert(
                    tk.END, "\nCorreção concluída com sucesso!\n")
                messagebox.showinfo(
                    "Sucesso", "Arquivo corrigido com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao corrigir o arquivo")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao corrigir arquivo: {str(e)}")

    def zip_rinex_files(self):
        file_path = self.selected_file.get()
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo para comprimir")
            return

        try:
            # Obtém o diretório e nome base do arquivo
            file_dir = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]

            # Lista para armazenar os arquivos encontrados
            rinex_files = []

            # Procura por arquivos com as extensões .??O, .??N e .??G
            extensions = ['O', 'N', 'G']
            for ext in extensions:
                pattern = os.path.join(file_dir, f"{base_name}.??{ext}")
                found_files = glob.glob(pattern)
                rinex_files.extend(found_files)

            if not rinex_files:
                messagebox.showerror(
                    "Erro", "Nenhum arquivo RINEX encontrado para compressão")
                return

            # Cria o nome do arquivo ZIP
            zip_filename = os.path.join(file_dir, f"{base_name}_RINEX.zip")

            # Cria o arquivo ZIP
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in rinex_files:
                    # Adiciona cada arquivo ao ZIP usando apenas o nome do arquivo (sem o caminho completo)
                    zipf.write(file, os.path.basename(file))

            self.result_text.insert(
                tk.END, f"\nArquivos comprimidos com sucesso em: {zip_filename}\n")
            self.result_text.insert(tk.END, "Arquivos incluídos:\n")
            for file in rinex_files:
                self.result_text.insert(
                    tk.END, f"- {os.path.basename(file)}\n")

            messagebox.showinfo("Sucesso", "Arquivos comprimidos com sucesso!")

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao comprimir arquivos: {str(e)}")


def main():
    root = tk.Tk()
    RinexGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
