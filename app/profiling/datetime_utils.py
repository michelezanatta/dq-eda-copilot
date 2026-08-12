from __future__ import annotations

import warnings

import pandas as pd

from app.config import settings

def clean_datetime_strings(series: pd.Series) -> pd.Series:
 return series.astype(str).str.strip().replace({"": None, "nan": None, "None": None})

def parse_datetime_series(series: pd.Series) -> pd.Series:
 cleaned = clean_datetime_strings(series)

 for fmt in settings.datetime_formats_to_try:
    parsed = pd.to_datetime(cleaned, format=fmt, errors="coerce")
    success_ratio = float(parsed.notna().mean()) if len(parsed) else 0.0

    if success_ratio >= 0.8:
        return parsed

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return pd.to_datetime(cleaned, errors="coerce") 