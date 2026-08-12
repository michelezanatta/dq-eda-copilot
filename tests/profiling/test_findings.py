import pandas as pd

from app.profiling.findings import generate_findings
from app.profiling.profiler import build_dataset_profile

def test_generate_findings_returns_list(sample_dataframe):
    profile = build_dataset_profile(sample_dataframe)
    findings = generate_findings(profile)

    assert isinstance(findings, list)

def test_generate_findings_detects_missingness():
    df = pd.DataFrame(
    {
    "a": [1, None, None, 4],
    "b": [1, 2, 3, 4],
    }
    )
    profile = build_dataset_profile(df)
    findings = generate_findings(profile)

    finding_types = [f.finding_type for f in findings]
    assert "dataset_missingness" in finding_types or "column_missingness" in finding_types

def test_generate_findings_detects_constant_column():
    df = pd.DataFrame(
    {
    "constant_col": ["X", "X", "X", "X"],
    "value": [1, 2, 3, 4],
    }
    )
    profile = build_dataset_profile(df)
    findings = generate_findings(profile)

    assert any(f.finding_type == "constant_column" for f in findings)

def test_generate_findings_detects_strong_correlation():
    df = pd.DataFrame(
    {
    "x": [1, 2, 3, 4, 5],
    "y": [2, 4, 6, 8, 10],
    }
    )
    profile = build_dataset_profile(df)
    findings = generate_findings(profile)

    assert any(f.finding_type == "strong_correlation" for f in findings)