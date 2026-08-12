from __future__ import annotations

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from app.config import settings
from app.profiling.correlations import compute_correlations
from app.profiling.type_inference import (
    detect_boolean_like,
    detect_free_text_like,
    detect_id_like,
    infer_logical_type,
)
from app.schemas import (
    BooleanColumnProfile,
    CategoricalColumnProfile,
    DatasetProfile,
    DatetimeColumnProfile,
    GenericColumnProfile,
    NumericColumnProfile,
)


from app.profiling.datetime_utils import parse_datetime_series

def _base_stats(series: pd.Series) -> dict:
    non_null = series.dropna()
    total_count = int(len(series))
    non_null_count = int(len(non_null))
    null_count = int(total_count - non_null_count)
    null_ratio = float(null_count / total_count) if total_count else 0.0
    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = float(unique_count / non_null_count) if non_null_count else 0.0
    is_constant = unique_count <= 1 and non_null_count > 0

    return {
        "non_null_count": non_null_count,
        "null_count": null_count,
        "null_ratio": null_ratio,
        "unique_count": unique_count,
        "unique_ratio": unique_ratio,
        "is_constant": is_constant,
    }

def _profile_boolean_column(series: pd.Series, column_name: str) -> BooleanColumnProfile:
    base = _base_stats(series)

    non_null = series.dropna()
    normalized = non_null.astype(str).str.strip().str.lower()

    true_values = {"true", "1", "yes", "y", "t"}
    false_values = {"false", "0", "no", "n", "f"}

    true_count = int(normalized.isin(true_values).sum())
    false_count = int(normalized.isin(false_values).sum())

    denominator = int(len(non_null))
    true_ratio = float(true_count / denominator) if denominator else 0.0
    false_ratio = float(false_count / denominator) if denominator else 0.0

    return BooleanColumnProfile(
        column=column_name,
        dtype=str(series.dtype),
        inferred_logical_type="boolean",
        true_count=true_count,
        false_count=false_count,
        true_ratio=true_ratio,
        false_ratio=false_ratio,
        **base,
    )

def _profile_numeric_column(series: pd.Series, column_name: str, inferred_logical_type: str) -> NumericColumnProfile:
    coerced = pd.to_numeric(series, errors="coerce")
    base = _base_stats(coerced)
    non_null = coerced.dropna()

    if non_null.empty:
        return NumericColumnProfile(
            column=column_name,
            dtype=str(series.dtype),
            inferred_logical_type=inferred_logical_type,
            **base,
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
    outlier_ratio = float(outlier_count / len(non_null)) if len(non_null) else 0.0

    zero_count = int((non_null == 0).sum())
    zero_ratio = float(zero_count / len(non_null)) if len(non_null) else 0.0

    warnings = []
    if inferred_logical_type == "numeric" and not is_numeric_dtype(series):
        warnings.append("Column was inferred as numeric from string/object values.")

    return NumericColumnProfile(
        column=column_name,
        dtype=str(series.dtype),
        inferred_logical_type=inferred_logical_type,
        warnings=warnings,
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
        **base,
    )

def _profile_datetime_column(series: pd.Series, column_name: str) -> DatetimeColumnProfile:
    parsed = parse_datetime_series(series)
    base = _base_stats(parsed)
    non_null = parsed.dropna()

    if non_null.empty:
        return DatetimeColumnProfile(
                    column=column_name,
                    dtype=str(series.dtype),
                    inferred_logical_type="datetime",
                    **base,
                    )

    min_date = non_null.min()
    max_date = non_null.max()
    range_days = int((max_date - min_date).days)

    warnings = []
    if str(series.dtype) not in ("datetime64[ns]", "datetime64[ns, UTC]"):
        warnings.append("Column was inferred as datetime from string/object values.")

    return DatetimeColumnProfile(
    column=column_name,
    dtype=str(series.dtype),
    inferred_logical_type="datetime",
    warnings=warnings,
    min_date=min_date.isoformat(),
    max_date=max_date.isoformat(),
    range_days=range_days,
    **base,
    )

def _profile_categorical_column(series: pd.Series, column_name: str, inferred_logical_type: str) -> CategoricalColumnProfile:
    base = _base_stats(series)
    non_null = series.dropna().astype(str)

    top_values = []
    avg_length = None
    min_length = None
    max_length = None

    if not non_null.empty:
        vc = non_null.value_counts(dropna=True).head(settings.max_top_values)
        top_values = [
            {
                "value": idx,
                "count": int(count),
                "ratio": float(count / len(non_null)),
            }
            for idx, count in vc.items()
        ]

        lengths = non_null.str.len()
        avg_length = float(lengths.mean()) if not lengths.empty else None
        min_length = int(lengths.min()) if not lengths.empty else None
        max_length = int(lengths.max()) if not lengths.empty else None

    return CategoricalColumnProfile(
        column=column_name,
        dtype=str(series.dtype),
        inferred_logical_type=inferred_logical_type,
        top_values=top_values,
        avg_length=avg_length,
        min_length=min_length,
        max_length=max_length,
        is_boolean_like=detect_boolean_like(series),
        is_id_like=detect_id_like(series),
        is_free_text_like=detect_free_text_like(series),
        **base,
    )

def _profile_other_column(series: pd.Series, column_name: str) -> GenericColumnProfile:
    base = _base_stats(series)
    return GenericColumnProfile(
        column=column_name,
        dtype=str(series.dtype),
        inferred_logical_type="other",
        **base,
    )

def build_dataset_profile(df: pd.DataFrame) -> DatasetProfile:
    row_count = int(df.shape[0])
    column_count = int(df.shape[1])
    total_cells = int(row_count * column_count)

    total_missing_cells = int(df.isna().sum().sum())
    missing_cell_ratio = float(total_missing_cells / total_cells) if total_cells else 0.0

    duplicate_row_count = int(df.duplicated().sum())
    duplicate_row_ratio = float(duplicate_row_count / row_count) if row_count else 0.0

    memory_usage_bytes = int(df.memory_usage(deep=True).sum())

    column_profiles = []

    numeric_columns = []
    categorical_columns = []
    datetime_columns = []
    boolean_columns = []
    other_columns = []
    constant_columns = []

    profiling_warnings = []

    for col in df.columns:
        column_name = str(col)
        series = df[col]
        inferred_type = infer_logical_type(series)

        if is_bool_dtype(series) or inferred_type == "boolean":
            profile = _profile_boolean_column(series, column_name)
            boolean_columns.append(column_name)

        elif is_numeric_dtype(series) or inferred_type == "numeric":
            profile = _profile_numeric_column(series, column_name, inferred_type)
            numeric_columns.append(column_name)

        elif inferred_type == "datetime":
            profile = _profile_datetime_column(series, column_name)
            datetime_columns.append(column_name)

        elif inferred_type in ("categorical", "categorical_id", "text"):
            profile = _profile_categorical_column(series, column_name, inferred_type)
            categorical_columns.append(column_name)

        else:
            profile = _profile_other_column(series, column_name)
            other_columns.append(column_name)

        if profile.is_constant:
            constant_columns.append(column_name)

        column_profiles.append(profile)

    correlations, truncated_correlations = compute_correlations(df)

    if truncated_correlations:
        profiling_warnings.append(
            "Correlation output was truncated or sampled due to dataset width/size guardrails."
        )

    columns_by_type = {
        "numeric": len(numeric_columns),
        "categorical": len(categorical_columns),
        "datetime": len(datetime_columns),
        "boolean": len(boolean_columns),
        "other": len(other_columns),
    }

    return DatasetProfile(
        row_count=row_count,
        column_count=column_count,
        total_cells=total_cells,
        total_missing_cells=total_missing_cells,
        missing_cell_ratio=missing_cell_ratio,
        duplicate_row_count=duplicate_row_count,
        duplicate_row_ratio=duplicate_row_ratio,
        memory_usage_bytes=memory_usage_bytes,
        columns_by_type=columns_by_type,
        constant_columns=constant_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        datetime_columns=datetime_columns,
        boolean_columns=boolean_columns,
        other_columns=other_columns,
        column_profiles=column_profiles,
        correlations=correlations,
        truncated_correlations=truncated_correlations,
        profiling_warnings=profiling_warnings,
    )