from __future__ import annotations

import pandas as pd

from app.schemas import NumericColumnProfile

def profile_numeric_column(series: pd.Series, column_name: str) -> NumericColumnProfile:
    s = series
    non_null = s.dropna()

    total_count = int(len(s))
    non_null_count = int(non_null.shape[0])
    null_count = int(total_count - non_null_count)
    null_ratio = float(null_count / total_count) if total_count else 0.0

    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = float(unique_count / non_null_count) if non_null_count else 0.0
    is_constant = unique_count <= 1 and non_null_count > 0

    if non_null_count == 0:
        return NumericColumnProfile(
            column=column_name,
            dtype=str(s.dtype),
            non_null_count=non_null_count,
            null_count=null_count,
            null_ratio=null_ratio,
            unique_count=unique_count,
            unique_ratio=unique_ratio,
            is_constant=is_constant,
        )

    desc = non_null.describe(percentiles=[0.25, 0.5, 0.75])

    q1 = float(desc["25%"])
    median = float(desc["50%"])
    q3 = float(desc["75%"])
    iqr = float(q3 - q1)

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outlier_mask = (non_null < lower_bound) | (non_null > upper_bound)
    outlier_count = int(outlier_mask.sum())
    outlier_ratio = float(outlier_count / non_null_count) if non_null_count else 0.0

    zero_count = int((non_null == 0).sum())
    zero_ratio = float(zero_count / non_null_count) if non_null_count else 0.0

    return NumericColumnProfile(
        column=column_name,
        dtype=str(s.dtype),
        non_null_count=non_null_count,
        null_count=null_count,
        null_ratio=null_ratio,
        unique_count=unique_count,
        unique_ratio=unique_ratio,
        is_constant=is_constant,
        mean=float(desc["mean"]),
        std=float(desc["std"]) if pd.notna(desc["std"]) else None,
        min=float(desc["min"]),
        p25=q1,
        median=median,
        p75=q3,
        max=float(desc["max"]),
        iqr=iqr,
        outlier_count_iqr=outlier_count,
        outlier_ratio_iqr=outlier_ratio,
        zero_count=zero_count,
        zero_ratio=zero_ratio,
    )