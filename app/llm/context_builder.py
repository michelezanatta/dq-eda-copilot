from __future__ import annotations

from app.config import settings
from app.schemas import DatasetProfile, Finding, QualityScoreResult

def build_llm_context(
    profile: DatasetProfile,
    findings: list[Finding],
    quality: QualityScoreResult,
    ) -> dict:
    top_findings = findings[: settings.llm_max_top_findings]

    compact_findings = []
    for f in top_findings:
        compact_findings.append(
        {
        "finding_type": f.finding_type,
        "severity": f.severity,
        "title": f.title,
        "message": f.message,
        "column": f.column,
        "metrics": f.metrics,
        "recommendation": f.recommendation,
        }
        )

    context = {
    "dataset_overview": {
    "row_count": profile.row_count,
    "column_count": profile.column_count,
    "missing_cell_ratio": profile.missing_cell_ratio,
    "duplicate_row_ratio": profile.duplicate_row_ratio,
    "columns_by_type": profile.columns_by_type,
    "constant_columns_count": len(profile.constant_columns),
    "truncated_correlations": profile.truncated_correlations,
    },
    "quality": {
    "quality_score": quality.quality_score,
    "quality_status": quality.quality_status,
    "severity_counts": quality.severity_counts,
    "total_findings": quality.total_findings,
    },
    "top_findings": compact_findings,
    "profiling_warnings": profile.profiling_warnings,
    }

    return context