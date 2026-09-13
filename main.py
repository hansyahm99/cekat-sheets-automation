"""
main.py
Orchestrator: loop ESL/ESC/EHL -> login+export -> transform -> push ke tab masing-masing.
"""

import os
import sys
import shutil
import traceback

from scraper import download_tracker
from transform import transform
from push_to_sheets import push

UNITS = ["ESL", "ESC", "EHL"]
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")


def get_credentials(unit: str) -> tuple[str, str]:
    username = os.environ[f"CEKAT_{unit}_USER"]
    password = os.environ[f"CEKAT_{unit}_PASS"]
    return username, password


def run():
    any_failed = False

    for unit in UNITS:
        print(f"=== Processing unit: {unit} ===")
        try:
            username, password = get_credentials(unit)
            filepath = download_tracker(username, password, unit, DOWNLOAD_DIR)
            print(f"[{unit}] File terdownload: {filepath}")

            df = transform(filepath)
            print(f"[{unit}] {len(df)} baris setelah cleaning.")
            push(worksheet_name=unit, df=df)

        except Exception as e:
            any_failed = True
            print(f"[{unit}] GAGAL: {e}")
            traceback.print_exc()

    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    run()
