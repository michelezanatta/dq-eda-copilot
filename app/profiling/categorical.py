from __future__ import annotations

import pandas as pd

from app.config import settings
from app.schemas import CategoricalColumnProfile

def profile_categorical_column(series: pd.Series, column_name: str) -> CategoricalColumnProfile:
    s = series
    non_null = s.dropna()

    total_count = int(len(s))
    non_null_count = int(non_null.shape[0])
    null_count = int(total_count - non_null_count)
    null_ratio = float(null_count / total_count) if total_count else 0.0

    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = float(unique_count / non_null_count) if non_null_count else 0.0
    is_constant = unique_count <= 1 and non_null_count > 0

    top_values = []
    if non_null_count > 0:
        vc = non_null.astype(str).value_counts(dropna=True).head(settings.max_top_values)
        top_values = [
            {
                "value": idx,
                "count": int(count),
                "ratio": float(count / non_null_count),
            }
            for idx, count in vc.items()
        ]

        lengths = non_null.astype(str).str.len()
        avg_length = float(lengths.mean()) if not lengths.empty else None
        min_length = int(lengths.min()) if not lengths.empty else None
        max_length = int(lengths.max()) if not lengths.empty else None
    else:
        avg_length = None
        min_length = None
        max_length = None

    return CategoricalColumnProfile(
        column=column_name,
        dtype=str(s.dtype),
        non_null_count=non_null_count,
        null_count=null_count,
        null_ratio=null_ratio,
        unique_count=unique_count,
        unique_ratio=unique_ratio,
        is_constant=is_constant,
        top_values=top_values,
        avg_length=avg_length,
        min_length=min_length,
        max_length=max_length,
    )