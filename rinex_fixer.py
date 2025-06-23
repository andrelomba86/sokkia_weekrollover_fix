#!/usr/bin/env python3

import subprocess
from pathlib import Path
from rinex_gpsweek import calculate_gpsw_correction
from bin.binary import get_gfzrnx_path
from logger import logger


class RinexFixer:
    def __init__(self):
        gfzrnx_path = get_gfzrnx_path()
        self.GFZRNX = gfzrnx_path
        # self.RINEX_DIR = rinex_dir
        self.SHIFT_WEEKS = 1024

    def run_command(self, cmd: list, error_msg: str) -> bool:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def process_rinex_file(self, filepath) -> bool:
        filepath = Path(filepath)
        filename = filepath.name
        outfile = f"{filepath}.CORRIGIDO"

        logger.notify(f"Processando arquivo: {filename}")

        try:

            shift = calculate_gpsw_correction(filepath)
            logger.notify("\n")
            logger.notify(f"Diferença de semanas calculada: {shift}")

            if Path(f"{filepath}.ORIGINAL").exists():
                logger.notify("\n")
                logger.notify(
                    f"\nErro: Foi encontrado o arquivo \"{filepath}.ORIGINAL\"")
                logger.notify(
                    "Verifique se o processo de correção já não foi realizado.\n")
                return False

            try:
                subprocess.run(
                    [self.GFZRNX, "-shift_gpsw", str(shift), "-finp", str(filepath),
                        "-fout", outfile, "-vo", "2"],
                    check=True, capture_output=True, text=True
                )
            except subprocess.CalledProcessError as e:
                log_file = open(f"{filepath}.gfzrnx.log", "w")
                log_file.write(e.stdout or "")
                log_file.write(e.stderr or "")
                log_file.close()
                logger.notify("\n")
                logger.notify(
                    f"Erro ao executar GFZRNX. Veja o log em {filepath}.gfzrnx.log")
                return False

            filepath.rename(f"{filepath}.ORIGINAL")
            logger.notify("\n")
            logger.notify(
                f"Arquivo original renomeado para: {filename}.ORIGINAL")

            Path(outfile).rename(filepath)
            logger.notify(f"Arquivo corrigido salvo como: {filename}")

            return True

        except subprocess.CalledProcessError as e:
            logger.notify(f"Saída de erro: {e.stderr}")
            return False
