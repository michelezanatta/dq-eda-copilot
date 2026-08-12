from __future__ import annotations

import pandas as pd

from app.schemas import DatetimeColumnProfile

def profile_datetime_column(series: pd.Series, column_name: str) -> DatetimeColumnProfile:
    s = pd.to_datetime(series, errors="coerce")
    non_null = s.dropna()

    total_count = int(len(s))
    non_null_count = int(non_null.shape[0])
    null_count = int(total_count - non_null_count)
    null_ratio = float(null_count / total_count) if total_count else 0.0

    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = float(unique_count / non_null_count) if non_null_count else 0.0
    is_constant = unique_count <= 1 and non_null_count > 0

    if non_null_count == 0:
        return DatetimeColumnProfile(
            column=column_name,
            dtype=str(series.dtype),
            non_null_count=non_null_count,
            null_count=null_count,
            null_ratio=null_ratio,
            unique_count=unique_count,
            unique_ratio=unique_ratio,
            is_constant=is_constant,
        )

    min_date = non_null.min()
    max_date = non_null.max()
    range_days = int((max_date - min_date).days)

    return DatetimeColumnProfile(
        column=column_name,
        dtype=str(series.dtype),
        non_null_count=non_null_count,
        null_count=null_count,
        null_ratio=null_ratio,
        unique_count=unique_count,
        unique_ratio=unique_ratio,
        is_constant=is_constant,
        min_date=min_date.isoformat(),
        max_date=max_date.isoformat(),
        range_days=range_days,
    )