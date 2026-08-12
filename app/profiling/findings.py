from __future__ import annotations

from app.config import settings
from app.schemas import (
    BooleanColumnProfile,
    CategoricalColumnProfile,
    DatasetProfile,
    Finding,
    NumericColumnProfile,
    )

def _severity_from_ratio(
    value: float,
    medium: float,
    high: float,
    critical: float,
    ) -> str | None:
    if value >= critical:
        return "critical"
    if value >= high:
        return "high"
    if value >= medium:
        return "medium"
    return None

def _rank_score(severity: str, impact: float = 1.0) -> float:
    severity_weights = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
    }
    return severity_weights.get(severity, 0.0) * impact

def generate_findings(profile: DatasetProfile) -> list[Finding]:
    findings: list[Finding] = []

    dataset_missing_severity = _severity_from_ratio(
    profile.missing_cell_ratio,
    settings.finding_missingness_medium,
    settings.finding_missingness_high,
    settings.finding_missingness_critical,
    )
    if dataset_missing_severity:
        findings.append(
        Finding(
        finding_type="dataset_missingness",
        severity=dataset_missing_severity,
        title="Dataset has notable missing values",
        message=f"Overall missing cell ratio is {profile.missing_cell_ratio:.2%}.",
        metrics={
        "missing_cell_ratio": profile.missing_cell_ratio,
        "total_missing_cells": profile.total_missing_cells,
        "total_cells": profile.total_cells,
        },
        recommendation="Review missing-data handling strategy and identify the most affected columns.",
        rank_score=_rank_score(dataset_missing_severity, 1.5),
        )
        )

    duplicate_severity = _severity_from_ratio(
    profile.duplicate_row_ratio,
    settings.finding_duplicate_rows_medium,
    settings.finding_duplicate_rows_high,
    settings.finding_duplicate_rows_critical,
    )
    if duplicate_severity:
        findings.append(
        Finding(
        finding_type="duplicate_rows",
        severity=duplicate_severity,
        title="Dataset contains duplicate rows",
        message=f"Duplicate row ratio is {profile.duplicate_row_ratio:.2%}.",
        metrics={
        "duplicate_row_count": profile.duplicate_row_count,
        "duplicate_row_ratio": profile.duplicate_row_ratio,
        },
        recommendation="Review deduplication keys and ingestion rules.",
        rank_score=_rank_score(duplicate_severity, 1.4),
        )
        )

    if profile.column_count > 200:
        findings.append(
        Finding(
        finding_type="wide_dataset",
        severity="medium",
        title="Dataset is wide",
        message=f"The dataset has {profile.column_count} columns, which may complicate analysis and maintenance.",
        metrics={"column_count": profile.column_count},
        recommendation="Review whether all columns are necessary and consider grouping related features.",
        rank_score=_rank_score("medium", 0.8),
        )
        )

    if profile.truncated_correlations:
        findings.append(
        Finding(
        finding_type="correlation_truncated",
        severity="low",
        title="Correlation analysis was truncated or sampled",
        message="Correlation analysis used guardrails due to dataset width or size.",
        metrics={"truncated_correlations": profile.truncated_correlations},
        recommendation="If needed, run a focused correlation analysis on a subset of columns.",
        rank_score=_rank_score("low", 0.5),
        )
        )

    for cp in profile.column_profiles:
        if cp.is_constant:
            findings.append(
            Finding(
            finding_type="constant_column",
            severity="medium",
            title="Constant column detected",
            message=f"Column '{cp.column}' has the same value for all non-null rows.",
            column=cp.column,
            metrics={
            "unique_count": cp.unique_count,
            "non_null_count": cp.non_null_count,
            },
            recommendation="Consider dropping this column unless it is required for traceability or filtering.",
            rank_score=_rank_score("medium", 1.2),
            )
            )

        null_severity = _severity_from_ratio(
        cp.null_ratio,
        settings.finding_missingness_medium,
        settings.finding_missingness_high,
        settings.finding_missingness_critical,
        )
        if null_severity:
            findings.append(
            Finding(
            finding_type="column_missingness",
            severity=null_severity,
            title="Column has missing values",
            message=f"Column '{cp.column}' has missing ratio {cp.null_ratio:.2%}.",
            column=cp.column,
            metrics={
            "null_count": cp.null_count,
            "null_ratio": cp.null_ratio,
            },
            recommendation="Check whether missing values are expected and define imputation or exclusion rules.",
            rank_score=_rank_score(null_severity, 1.3),
            )
            )

        if isinstance(cp, NumericColumnProfile):
            outlier_ratio = cp.outlier_ratio_iqr or 0.0
            outlier_severity = _severity_from_ratio(
            outlier_ratio,
            settings.finding_outlier_ratio_medium,
            settings.finding_outlier_ratio_high,
            settings.finding_outlier_ratio_critical,
            )
            if outlier_severity:
                findings.append(
                Finding(
                finding_type="numeric_outliers",
                severity=outlier_severity,
                title="Numeric column has outliers",
                message=f"Column '{cp.column}' has IQR outlier ratio {outlier_ratio:.2%}.",
                column=cp.column,
                metrics={
                "outlier_count_iqr": cp.outlier_count_iqr,
                "outlier_ratio_iqr": outlier_ratio,
                },
                recommendation="Review whether these values are valid extremes, data errors, or candidates for capping/transformation.",
                rank_score=_rank_score(outlier_severity, 1.2),
                )
                )

            if cp.zero_ratio is not None and cp.zero_ratio > 0.95:
                findings.append(
                Finding(
                finding_type="mostly_zero_numeric",
                severity="medium",
                title="Numeric column is mostly zero",
                message=f"Column '{cp.column}' has zero ratio {cp.zero_ratio:.2%}.",
                column=cp.column,
                metrics={"zero_ratio": cp.zero_ratio},
                recommendation="Check whether this field has low information value or is sparsely populated by design.",
                rank_score=_rank_score("medium", 0.9),
                )
                )

        if isinstance(cp, CategoricalColumnProfile):
            if cp.unique_ratio >= settings.finding_high_cardinality_ratio and cp.non_null_count > 20:
                findings.append(
                Finding(
                finding_type="high_cardinality_categorical",
                severity="medium",
                title="Categorical column has high cardinality",
                message=f"Column '{cp.column}' has unique ratio {cp.unique_ratio:.2%}.",
                column=cp.column,
                metrics={
                "unique_count": cp.unique_count,
                "unique_ratio": cp.unique_ratio,
                },
                recommendation="Check whether this is actually an ID/code field or whether values should be standardized.",
                rank_score=_rank_score("medium", 1.0),
                )
                )

            if cp.is_id_like:
                findings.append(
                Finding(
                finding_type="id_like_column",
                severity="low",
                title="ID-like column detected",
                message=f"Column '{cp.column}' appears to behave like an identifier.",
                column=cp.column,
                metrics={"unique_ratio": cp.unique_ratio},
                recommendation="Avoid using this column for statistical pattern interpretation unless it has business meaning.",
                rank_score=_rank_score("low", 0.8),
                )
                )

            if cp.is_free_text_like:
                findings.append(
                Finding(
                finding_type="free_text_column",
                severity="low",
                title="Free-text column detected",
                message=f"Column '{cp.column}' appears to contain free text.",
                column=cp.column,
                metrics={
                "avg_length": cp.avg_length,
                "unique_ratio": cp.unique_ratio,
                },
                recommendation="Handle this column separately from standard categorical profiling.",
                rank_score=_rank_score("low", 0.7),
                )
                )

        if isinstance(cp, BooleanColumnProfile):
            dominant_ratio = max(cp.true_ratio, cp.false_ratio)
            if dominant_ratio >= settings.finding_near_constant_ratio and cp.non_null_count > 0:
                findings.append(
                Finding(
                finding_type="skewed_boolean",
                severity="low",
                title="Boolean column is highly skewed",
                message=f"Column '{cp.column}' is dominated by one value ({dominant_ratio:.2%}).",
                column=cp.column,
                metrics={
                "true_ratio": cp.true_ratio,
                "false_ratio": cp.false_ratio,
                },
                recommendation="Check whether this field carries enough signal for downstream use.",
                rank_score=_rank_score("low", 0.7),
                )
                )

    for corr in profile.correlations:
        abs_corr = float(corr.get("abs_correlation", 0.0))

        severity = None
        if abs_corr >= settings.finding_strong_correlation_critical:
            severity = "critical"
        elif abs_corr >= settings.finding_strong_correlation_high:
            severity = "high"

        if severity:
            findings.append(
            Finding(
            finding_type="strong_correlation",
            severity=severity,
            title="Strong correlation detected",
            message=(
            f"Columns '{corr['column_a']}' and '{corr['column_b']}' "
            f"have correlation {corr['correlation']:.3f}."
            ),
            metrics=corr,
            recommendation="Review whether these variables are redundant, derived from each other, or at risk of leakage.",
            rank_score=_rank_score(severity, 1.6),
            )
        )

    findings.sort(key=lambda f: f.rank_score, reverse=True)
    return findings