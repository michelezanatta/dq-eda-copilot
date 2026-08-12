from __future__ import annotations

from app.config import settings
from app.schemas import Finding, QualityScoreResult

def compute_quality_score(findings: list[Finding]) -> QualityScoreResult:
    severity_counts = {
    "low": 0,
    "medium": 0,
    "high": 0,
    "critical": 0,
    }

    penalties = {
    "low": 0.0,
    "medium": 0.0,
    "high": 0.0,
    "critical": 0.0,
    }

    for finding in findings:
        severity = finding.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        if severity == "low":
            penalties["low"] += settings.quality_penalty_low
        elif severity == "medium":
            penalties["medium"] += settings.quality_penalty_medium
        elif severity == "high":
            penalties["high"] += settings.quality_penalty_high
        elif severity == "critical":
            penalties["critical"] += settings.quality_penalty_critical

    total_penalty = sum(penalties.values())
    quality_score = max(0.0, 100.0 - total_penalty)

    if quality_score >= settings.quality_status_good_min:
        quality_status = "good"
    elif quality_score >= settings.quality_status_fair_min:
        quality_status = "fair"
    else:
        quality_status = "poor"

    return QualityScoreResult(
    quality_score=round(quality_score, 2),
    quality_status=quality_status,
    severity_counts=severity_counts,
    total_findings=len(findings),
    penalties={k: round(v, 2) for k, v in penalties.items()},
    )