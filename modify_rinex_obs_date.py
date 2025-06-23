#!/usr/bin/env python3

import sys
from datetime import datetime
import re
import os
import glob
import zipfile


def modify_rinex_observation_date(input_file, output_file, new_date_str):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()

    # Flags to track if first and last obs times were modified
    first_obs_modified = False
    last_obs_modified = False

    for i, line in enumerate(lines):
        if "TIME OF FIRST OBS" in line or "TIME OF LAST OBS" in line:
            label = "TIME OF FIRST OBS" if "TIME OF FIRST OBS" in line else "TIME OF LAST OBS"
            original_fields = line[:43].strip()
            parts = list(map(float, original_fields.split()))
            original_datetime = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                                         int(parts[3]), int(parts[4]), int(parts[5]))
            updated_datetime = datetime.combine(
                new_date, original_datetime.time())

            new_line = f"{updated_datetime.year:>6}{updated_datetime.month:>6}{updated_datetime.day:>6}" \
                       f"{updated_datetime.hour:>6}{updated_datetime.minute:>6}{updated_datetime.second:13.7f}     GPS         {label}\n"
            lines[i] = new_line

            if label == "TIME OF FIRST OBS":
                first_obs_modified = True
            else:
                last_obs_modified = True

        if first_obs_modified and last_obs_modified:
            break

    # Modify epochs in observation section
    in_body = False
    for i, line in enumerate(lines):
        if "END OF HEADER" in line:
            in_body = True
            continue

        if in_body and line.startswith(' '):
            # match = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)", line)

            match = re.match(
                r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)\s+(.+)", line)
            if match:
                y, mo, d, h, mi, s, sats = match.groups()
                original_time = datetime(int(y), int(mo), int(
                    d), int(h), int(mi), int(float(s)))
                updated_time = datetime.combine(new_date, original_time.time())

                updated_line = f"{updated_time.strftime('%y'):>3}{updated_time.strftime('%m'):>3}{updated_time.strftime('%d'):>3}" \
                    f"{h:>3}{mi:>3} {s:>10}  {sats}\n"
                # f"{updated_time.hour:>4}{updated_time.minute:>6}{updated_time.second + updated_time.microsecond / 1e6:13.7f}" + line[43:]
                lines[i] = updated_line

    with open(output_file, 'w') as f:
        f.writelines(lines)

    print(f"Modified file saved as: {output_file}")


def zip_rinex_family_files(input_file):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    directory = os.path.dirname(os.path.abspath(input_file))

    matching_files = glob.glob(os.path.join(
        directory, base_name + ".[0-9][0-9][G,N,O]"))

    if not matching_files:
        print("No matching RINEX files found to zip.")
        return

    zip_name = os.path.join(directory, base_name + ".zip")

    # Remove existing zip file if it exists
    if os.path.exists(zip_name):
        os.remove(zip_name)
        print(f"Removed existing zip archive: {zip_name}")

    # Create zip file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in matching_files:
            zipf.write(file, arcname=os.path.basename(file))
            print(f"Added to zip: {file}")

    print(f"\nCreated new zip archive: {zip_name}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python rinex_date_edit.py input_file.obs YYYY-MM-DD")
        sys.exit(1)

    input_file = sys.argv[1]
    new_date_str = sys.argv[2]
    output_file = input_file.replace(".obs", "_dated.obs")

    modify_rinex_observation_date(input_file, output_file, new_date_str)
    zip_rinex_family_files(input_file)


if __name__ == "__main__":
    main()
