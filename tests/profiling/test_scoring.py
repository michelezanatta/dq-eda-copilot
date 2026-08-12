from app.profiling.scoring import compute_quality_score
from app.schemas import Finding

def test_compute_quality_score_empty_findings():
    result = compute_quality_score([])

    assert result.quality_score == 100.0
    assert result.quality_status == "good"
    assert result.total_findings == 0

def test_compute_quality_score_with_findings():
    findings = [
    Finding(
    finding_type="column_missingness",
    severity="medium",
    title="Missing values",
    message="Column has missing values",
    ),
    Finding(
    finding_type="strong_correlation",
    severity="high",
    title="Strong correlation",
    message="Two columns are strongly correlated",
    ),
    ]

    result = compute_quality_score(findings)

    assert result.total_findings == 2
    assert result.severity_counts["medium"] == 1
    assert result.severity_counts["high"] == 1
    assert result.quality_score < 100.0

def test_compute_quality_score_poor_status():
    findings = [
    Finding(
    finding_type=f"critical_issue_{i}",
    severity="critical",
    title="Critical issue",
    message="Critical issue found",
    )
    for i in range(6)
    ]

    result = compute_quality_score(findings)

    assert result.quality_status == "poor"