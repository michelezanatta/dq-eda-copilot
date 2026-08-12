from __future__ import annotations

import pandas as pd

from app.config import settings

def compute_correlations(df: pd.DataFrame) -> tuple[list[dict], bool]:
    numeric_df = df.select_dtypes(include=["number"]).copy()

    if numeric_df.shape[1] < 2:
        return [], False

    truncated = False

    if numeric_df.shape[1] > settings.max_numeric_columns_in_correlation_output:
        numeric_df = numeric_df.iloc[:, : settings.max_numeric_columns_in_correlation_output]
        truncated = True

    if numeric_df.shape[1] > settings.max_columns_for_full_correlation and len(numeric_df) > settings.profiling_sample_rows_for_wide_datasets:
        numeric_df = numeric_df.sample(
            n=settings.profiling_sample_rows_for_wide_datasets,
            random_state=42,
        )
        truncated = True

    corr_matrix = numeric_df.corr(method=settings.correlation_method)
    cols = corr_matrix.columns.tolist()

    results = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            col_a = cols[i]
            col_b = cols[j]
            corr_value = corr_matrix.loc[col_a, col_b]

            if pd.isna(corr_value):
                continue

            corr_value = float(corr_value)
            if abs(corr_value) >= settings.correlation_min_abs_threshold:
                results.append(
                    {
                        "column_a": col_a,
                        "column_b": col_b,
                        "correlation": corr_value,
                        "abs_correlation": abs(corr_value),
                    }
                )

    results.sort(key=lambda x: x["abs_correlation"], reverse=True)

    if len(results) > settings.max_correlation_pairs:
        results = results[: settings.max_correlation_pairs]
        truncated = True

    return results, truncated