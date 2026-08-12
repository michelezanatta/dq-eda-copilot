from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse

from app.ingestion.loader import load_dataframe_from_bytes
from app.ingestion.validators import IngestionValidationError
from app.llm.provider import generate_llm_report
from app.monitoring.request_log import log_analysis_event
from app.profiling.findings import generate_findings
from app.profiling.profiler import build_dataset_profile
from app.profiling.scoring import compute_quality_score
from app.reporting.html_report import render_html_report
from app.schemas import AnalysisResult, AnalyzeResponse

router = APIRouter()

def _run_analysis(df, ingestion_result) -> AnalysisResult:
    profile = build_dataset_profile(df)
    findings = generate_findings(profile)
    quality = compute_quality_score(findings)
    llm_report, llm_execution = generate_llm_report(profile, findings, quality)

    return AnalysisResult(
    ingestion=ingestion_result,
    profile=profile,
    findings=findings,
    quality=quality,
    llm_report=llm_report,
    llm_execution=llm_execution,
    )

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: Request, file: UploadFile = File(...)) -> AnalyzeResponse:
    try:
        content = await file.read()
        df, ingestion_result = load_dataframe_from_bytes(file.filename, content)
        result = _run_analysis(df, ingestion_result)

        log_analysis_event(
        { "filename": result.ingestion.metadata.filename,
        "file_format": result.ingestion.metadata.file_format,
        "size_bytes": result.ingestion.metadata.size_bytes,
        "row_count": result.ingestion.row_count,
        "column_count": result.ingestion.column_count,
        "quality_score": result.quality.quality_score,
        "quality_status": result.quality.quality_status,
        "total_findings": result.quality.total_findings,
        "llm_enabled": result.llm_execution.enabled,
        "llm_mode": result.llm_execution.mode,
        "llm_used_fallback": result.llm_execution.used_fallback,
        "llm_success": result.llm_execution.success,
        "llm_call_count": result.llm_execution.call_count,
        "client_host": request.client.host if request.client else None,
        }
        )

        return AnalyzeResponse(**result.model_dump())

    except IngestionValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/analyze/report/html", response_class=HTMLResponse)
async def analyze_report_html(file: UploadFile = File(...)) -> HTMLResponse:
    try:
        content = await file.read()
        df, ingestion_result = load_dataframe_from_bytes(file.filename, content)
        result = _run_analysis(df, ingestion_result)
        html = render_html_report(result)
        return HTMLResponse(content=html, status_code=200)
    except IngestionValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")