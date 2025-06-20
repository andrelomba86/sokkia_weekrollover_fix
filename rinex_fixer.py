#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from rinex_gpsweek import calculate_gpsw_correction
from utils.binary_manager import get_gfzrnx_path


class RinexFixer:
    def __init__(self, rinex_dir="./arquivos"):
        gfzrnx_path = get_gfzrnx_path()
        self.GFZRNX = gfzrnx_path
        self.RINEX_DIR = rinex_dir
        self.SHIFT_WEEKS = 1024

    def run_command(self, cmd: list, error_msg: str) -> bool:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def process_rinex_file(self, filepath: Path, text_widget=None) -> bool:
        filename = filepath.name
        outfile = f"{filepath}.CORRIGIDO"

        if text_widget:
            text_widget.insert("end", f"Processando arquivo: {filename}\n")

        try:
            shift, dados = calculate_gpsw_correction(filepath)

            if text_widget:
                text_widget.insert(
                    "end", f"\nDiferença de semanas detectada: {shift}\n")
                # text_widget.insert("end", f"📅 Primeira observação: {dados['file']['epo_first']}\n")
                # text_widget.insert("end", f"🔢 Semana registrada: {dados['file']['epo_first']}\n")

            if Path(f"{filepath}.ORIGINAL").exists():
                if text_widget:
                    text_widget.insert(
                        "end", f"\nErro: Foi encontrado o arquivo \"{filepath}.ORIGINAL\".\nVerifique se o processo de correção já não foi realizado.\n")
                return False

            if not self.run_command(
                [self.GFZRNX, "-shift_gpsw", str(shift), "-finp", str(filepath),
                 "-fout", outfile, "-vo", "2"],
                f"Falha ao corrigir: {filename}"
            ):
                return False

            filepath.rename(f"{filepath}.ORIGINAL")
            if text_widget:
                text_widget.insert(
                    "end", f"\nArquivo original renomeado para: {filename}.ORIGINAL\n")

            Path(outfile).rename(filepath)
            if text_widget:
                text_widget.insert(
                    "end", f"Arquivo corrigido salvo como: {filename}\n")

            return True

        except subprocess.CalledProcessError as e:
            if text_widget:
                text_widget.insert(
                    "end", f"\nErro ao processar {filename}: {e}\n")
                text_widget.insert("end", f"Saída de erro: {e.stderr}\n")
            return False
