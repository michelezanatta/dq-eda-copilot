from app.llm.provider import generate_llm_report
from app.profiling.findings import generate_findings
from app.profiling.profiler import build_dataset_profile
from app.profiling.scoring import compute_quality_score
from app.reporting.html_report import render_html_report
from app.schemas import AnalysisResult, FileMetadata, IngestionResult

def test_render_html_report(sample_dataframe):
    profile = build_dataset_profile(sample_dataframe)
    findings = generate_findings(profile)
    quality = compute_quality_score(findings)
    llm_report, llm_execution = generate_llm_report(profile, findings, quality)

    ingestion = IngestionResult(
    metadata=FileMetadata(
    filename="sample.csv",
    file_format="csv",
    size_bytes=123,
    ),
    row_count=sample_dataframe.shape[0],
    column_count=sample_dataframe.shape[1],
    columns=list(sample_dataframe.columns),
    )

    result = AnalysisResult(
    ingestion=ingestion,
    profile=profile,
    findings=findings,
    quality=quality,
    llm_report=llm_report,
    llm_execution=llm_execution,
    )

    html = render_html_report(result)

    assert "<html" in html.lower()
    assert "Data Quality Report" in html
    assert "sample.csv" in html
    assert "LLM Interpretation" in html