from __future__ import annotations

import pandas as pd
from pandas.api.types import (
 is_bool_dtype,
 is_datetime64_any_dtype,
 is_numeric_dtype,
)

from app.config import settings
from app.profiling.datetime_utils import parse_datetime_series

BOOLEAN_TRUE_VALUES = {"true", "1", "yes", "y", "t"}
BOOLEAN_FALSE_VALUES = {"false", "0", "no", "n", "f"}

def _safe_non_null(series: pd.Series) -> pd.Series:
 return series.dropna()

def detect_boolean_like(series: pd.Series) -> bool:
 if is_bool_dtype(series):
    return True

 non_null = _safe_non_null(series)
 if non_null.empty:
    return False

 normalized = non_null.astype(str).str.strip().str.lower()
 valid = normalized.isin(BOOLEAN_TRUE_VALUES | BOOLEAN_FALSE_VALUES)
 ratio = float(valid.mean()) if len(valid) else 0.0
 return ratio >= settings.boolean_like_detection_threshold

def detect_numeric_like(series: pd.Series) -> bool:
    if is_numeric_dtype(series):
        return True

    non_null = _safe_non_null(series)
    if non_null.empty:
        return False

    converted = pd.to_numeric(non_null.astype(str).str.strip(), errors="coerce")
    ratio = float(converted.notna().mean()) if len(non_null) else 0.0
    return ratio >= settings.numeric_like_detection_threshold

def detect_datetime_like(series: pd.Series) -> bool:
    if is_datetime64_any_dtype(series):
        return True

    non_null = _safe_non_null(series)
    if non_null.empty:
        return False

    parsed = parse_datetime_series(non_null)
    ratio = float(parsed.notna().mean()) if len(non_null) else 0.0
    return ratio >= settings.datetime_detection_threshold

def detect_id_like(series: pd.Series) -> bool:
    non_null = _safe_non_null(series)
    if non_null.empty:
        return False

    as_str = non_null.astype(str).str.strip()
    uniqueness_ratio = float(as_str.nunique(dropna=True) / len(as_str)) if len(as_str) else 0.0

    avg_length = float(as_str.str.len().mean()) if len(as_str) else 0.0
    has_spaces_ratio = float(as_str.str.contains(r"\s", regex=True).mean()) if len(as_str) else 0.0

    return (
    uniqueness_ratio >= settings.id_uniqueness_ratio_threshold
    and avg_length < settings.free_text_avg_length_threshold
    and has_spaces_ratio < 0.2
    )

def detect_free_text_like(series: pd.Series) -> bool:
    non_null = _safe_non_null(series)
    if non_null.empty:
        return False

    as_str = non_null.astype(str)
    avg_length = float(as_str.str.len().mean()) if len(as_str) else 0.0
    uniqueness_ratio = float(as_str.nunique(dropna=True) / len(as_str)) if len(as_str) else 0.0

    return (
    avg_length >= settings.free_text_avg_length_threshold
    and uniqueness_ratio >= settings.free_text_uniqueness_ratio_threshold
    )

def infer_logical_type(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"

    if is_numeric_dtype(series):
        return "numeric"

    if is_datetime64_any_dtype(series):
        return "datetime"

    if detect_boolean_like(series):
        return "boolean"

    if detect_numeric_like(series):
        return "numeric"

    if detect_datetime_like(series):
        return "datetime"

    if detect_id_like(series):
        return "categorical_id"

    if detect_free_text_like(series):
        return "text"

    return "categorical"