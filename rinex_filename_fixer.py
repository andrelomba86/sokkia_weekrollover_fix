#!/bin/python3

import json
import subprocess
from datetime import datetime, timedelta
from bin.binary import get_gfzrnx_path
from logger import logger
import os
import glob


def format_date_from_rinex(date_str):
    """
    Converts a RINEX date string in the format 'YYYY MM DD hh mm ss.ssssss' to a datetime object.
    Truncates or pads the fractional seconds to 6 digits if necessary.
    """
    date_str_parts = date_str.strip().split()
    seconds = date_str_parts[-1]

    if '.' in seconds:
        seconds_integer, frac = seconds.split('.')
        frac = frac[:6].ljust(6, '0')  # Truncate or pads to 6 digits
        date_str_parts[-1] = f"{seconds_integer}.{frac}"
    else:
        date_str_parts[-1] = f"{seconds}.000000"

    fixed_date_str = ' '.join(date_str_parts)
    fixed_date = datetime.strptime(fixed_date_str, "%Y %m %d %H %M %S.%f")

    return fixed_date


def extract_gfzrnx_metadata(rinex_file):
    gfzrnx_path = get_gfzrnx_path()
    logger.debug(f"Running {gfzrnx_path} on {rinex_file}")
    try:
        command = [gfzrnx_path, "-finp", rinex_file, "-meta", "basic:json"]
        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar gfzrnx: {e.stderr}")
        raise
    return json.loads(result.stdout)


def calculate_day_from_year(date_time):
    start_of_year = datetime(date_time.year, 1, 1)
    delta = date_time - start_of_year
    return delta.days + 1  # +1 because January 1st is day 1


def weekrollover_fix_date(date_time):

    gps_epoch = datetime(1980, 1, 6)
    weeks_since_epoch = (date_time - gps_epoch).days // 7
    # Cada rollover ocorre a cada 1024 semanas
    number_of_rollovers = weeks_since_epoch // 1024

    if number_of_rollovers == 0:
        return date_time

    number_of_weeks = number_of_rollovers * 1024
    new_date_time = date_time + timedelta(weeks=number_of_weeks)
    return new_date_time


def rename_rinex_files(old_filename, new_filename, dir_path):
    logger.notify(
        f"Renomeando arquivos para {new_filename}...")
    logger.debug(
        f"Old filenames: {old_filename} / New filenames: {new_filename}")
    pattern = os.path.join(dir_path, f"{old_filename}.[0-9][0-9][G,N,O]")
    rinex_files = glob.glob(pattern)
    logger.debug(
        f"Files found to rename: {rinex_files} \n\t...in dir path: ${dir_path}")
    if not rinex_files:
        logger.notify("Erro: Nenhum arquivo RINEX encontrado para compressão")
        return

    for old_file in rinex_files:
        try:
            new_ext = os.path.splitext(old_file)[1]
            new_filepath = os.path.join(dir_path, f"{new_filename}{new_ext}")
            os.rename(old_file, new_filepath)
            logger.notify(
                f"Arquivo renomeado: {os.path.basename(old_file)} -> {os.path.basename(new_filepath)}")
        except Exception as e:
            logger.error(e)
            logger.notify(
                f"Erro ao renomear {os.path.basename(old_file)}: {e}")


# Variável global para station_id, pode ser definida externamente
station_id = "SSTR"


def rinex_filename_fixer(rinex_file, station_id_override=None):
    """
    Fix days from rinex file name
    """
    try:
        logger.notify("Verificando se é necessário renomear os arquivos...")
        data = extract_gfzrnx_metadata(rinex_file)
        gps_date_rinex = data["file"]["epo_first"]
        logger.debug(f"GPS Date on found on rinex file: {gps_date_rinex}")
        gps_date = format_date_from_rinex(gps_date_rinex)
        fixed_date = weekrollover_fix_date(gps_date)
        if (fixed_date > datetime.today()):
            logger.debug(f"Calculated date: {fixed_date}")
            raise ValueError(
                "It seems that the file already has an updated date.")
        day_of_year = str(calculate_day_from_year(fixed_date)).zfill(3)
        logger.debug(
            f"Calculated date: {fixed_date} / day of the year: {day_of_year}")

        # Usa station_id passado como argumento, senão usa o global
        sid = station_id_override if station_id_override else station_id

        old_filename = os.path.splitext(os.path.basename(rinex_file))[0]
        new_filename = f"{sid}{day_of_year}0"

        if (old_filename == new_filename):
            logger.notify("Os arquivos não serão renomeados")
            return new_filename
        path = os.path.dirname(rinex_file)
        rename_rinex_files(old_filename, new_filename, path)

        return new_filename
    except Exception as e:
        logger.notify(f"Erro ao corrigir o nome do arquivo RINEX: {e}")
        logger.error(e)
        return


# def main():
#     file = "./files/00062970.25O"
#     # file = "./files/00451420.25O.ORIGINAL"
#     rinex_filename_fixer(file)


# if __name__ == "__main__":
#     main()
