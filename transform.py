"""
transform.py
Cleaning data hasil scrape Cekat tracker pakai pandas.
"""

import pandas as pd
import numpy as np

DATE_LIKE_COLUMNS = [
    "created_at,
    "Tanggal Lead Masuk",
    "Label Cold",
    "Label Warm",
    "Label Hot",
    "Book",
    "Visit",
    "Visit Timestamp",
    "Convert",
    "Spam",
    "Out of Area",
    "Remarketing",
    "No Response",
    "Transfer to Telesales",
]

def read_export(filepath: str) -> pd.DataFrame:
    """Baca file xlsx hasil export Cekat. Phone dipaksa string biar gak jadi scientific notation."""
    df = pd.read_excel(filepath, dtype={"Phone": str})
    return df

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.replace(r"^\s*$", np.nan, regex=True)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    if "Phone" in df.columns:
        df["Phone"] = (
            df["Phone"]
            .astype(str).str.replace(r"\.0$", "", regex=True).replace("nan", np.nan)
        )

    for col in DATE_LIKE_COLUMNS:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce", format="mixed", dayfirst=True)
            df[col] = parsed.dt.strftime("%Y-%m-$d %H:%M").fillna(df[col])

    if "Phone" in df.columns:
        df = df.drop_duplicates(subnet=["Phone"], keep="last")

    df = df.reset_index(drop=True)
    return df

def transform(filepath: str) -> pd.DataFrame:
    """Entry point dipanggil dari main.py"""
    df = read_export(filepath)
    return clean_dataframe(df)