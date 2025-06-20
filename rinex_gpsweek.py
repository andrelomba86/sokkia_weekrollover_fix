#!/bin/python3

"""
Module for calculating GPS week corrections in RINEX files
Provides functions to extract metadata and calculate GPS week shifts
"""

import json
import subprocess
from datetime import datetime, timedelta
from utils.binary_manager import get_gfzrnx_path


def gps_week_from_date(date_str):
    partes = date_str.strip().split()
    segundos = partes[-1]

    # If the fractional second has more than 6 digits, truncate to 6
    if '.' in segundos:
        segundos_base, frac = segundos.split('.')
        frac = frac[:6].ljust(6, '0')  # Truncate or pad to 6 digits
        partes[-1] = f"{segundos_base}.{frac}"
    else:
        partes[-1] = f"{segundos}.000000"

    date_str_corrigido = ' '.join(partes)

    gps_start = datetime(1980, 1, 6)  # week rollover initial date
    obs_time = datetime.strptime(date_str_corrigido, "%Y %m %d %H %M %S.%f")
    delta_days = (obs_time - gps_start).days
    week = delta_days // 7
    return week


def extract_metadata_gfzrnx(rinex_file):
    gfzrnx_path = get_gfzrnx_path()
    command = [gfzrnx_path, "-finp", rinex_file, "-meta", "basic:json"]
    result = subprocess.run(
        command, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def calculate_gpsw_correction(rinex_file):
    """
    Calculates the GPS week correction needed for a RINEX file
    Returns:
        tuple: (shift_gpsw, metadata_data)
    """
    data = extract_metadata_gfzrnx(rinex_file)

    # Extracts the date of the first observation
    first_obs_date = data["file"]["epo_first"]
    obs_week = gps_week_from_date(first_obs_date)

    # File registration date
    file_registration_date = data["file"]["epo_first_name"]
    registration_week = gps_week_from_date(file_registration_date)

    shift = registration_week - obs_week

    return shift, data


def calculate_year_gpsw_correction(year):
    epoch = datetime(1980, 1, 6)  # GPS Epoch
    date = datetime(year, 1, 1)

    week_number = (date - epoch).days // 7

    if week_number > 1023:
        correction = (week_number // 1024) * 1024
        return correction
    else:
        return 0
