"""
push_to_sheets.py
Push dataframe ke satu tab Google Sheets, overwrite (clear -> write ulang).
"""

import json
import os

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_client() -> gspread.Client:
    sa_key_json = os.environ["GCP_SA_KEY"]
    sa_info = json.loads(sa_key_json)
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return gspread.authorize(creds)


def push(worksheet_name: str, df: pd.DataFrame):
    """
    Overwrite isi tab `worksheet_name` dengan isi df.
    Kalau df kosong, tab tetap di-clear (biar gak nyisain data basi).
    """
    client = _get_client()
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sh = client.open_by_key(spreadsheet_id)

    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=30)

    ws.clear()

    if df.empty:
        print(f"[{worksheet_name}] Data kosong, tab dikosongkan.")
        return

    # header + rows, semua di-cast ke string biar aman dikirim ke Sheets API
    values = [df.columns.tolist()] + df.astype(str).values.tolist()
    ws.update(values, value_input_option="USER_ENTERED")
    print(f"[{worksheet_name}] {len(df)} baris berhasil di-push.")
