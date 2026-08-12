from __future__ import annotations

import json
from typing import Optional

from app.config import settings
from app.llm.context_builder import build_llm_context
from app.llm.output_schema import LLMReportSchema
from app.schemas import (
 DatasetProfile,
 Finding,
 LLMExecutionInfo,
 LLMReport,
 QualityScoreResult,
)

def _build_fallback_report(
    profile: DatasetProfile,
    findings: list[Finding],
    quality: QualityScoreResult,
    ) -> LLMReport:
    top_findings = findings[:5]

    if not top_findings:
        summary = (
        f"The dataset contains {profile.row_count} rows and {profile.column_count} columns. "
        f"No major issues were detected by the deterministic quality checks."
        )
        top_issues = ["No major findings detected."]
        overall_assessment = (
        f"The dataset received a quality score of {quality.quality_score} ({quality.quality_status}). "
        f"Overall quality appears stable based on the implemented profiling rules."
        )
        recommended_actions = [
        "Review a sample of records to confirm the absence of hidden business-rule issues.",
        "Proceed with downstream analysis while monitoring future data drift.",
        ]
    else:
        summary = (
        f"The dataset contains {profile.row_count} rows and {profile.column_count} columns. "
        f"It received a quality score of {quality.quality_score} ({quality.quality_status}). "
        f"The most important issues concern {', '.join([f.title.lower() for f in top_findings[:3]])}."
        )
        top_issues = [
        f"{f.severity.upper()}: {f.title} — {f.message}"
        for f in top_findings
        ]
        overall_assessment = (
        f"The deterministic analysis suggests an overall {quality.quality_status} data quality status. "
        f"The main risk areas are concentrated in the highest-ranked findings, especially where missingness, "
        f"duplicates, outliers, or structural anomalies may affect analytical reliability."
        )
    recommended_actions = []
    for f in top_findings[:5]:
        if f.recommendation and f.recommendation not in recommended_actions:
            recommended_actions.append(f.recommendation)

    if not recommended_actions:
        recommended_actions = [
        "Review the top findings and prioritize remediation based on severity and business impact."
        ]

    return LLMReport(
    summary=summary,
    top_issues=top_issues,
    overall_assessment=overall_assessment,
    recommended_actions=recommended_actions,
    )

def _call_ollama_once(context: dict) -> tuple[Optional[LLMReport], Optional[str]]:
    try:
        import requests
    except Exception:
        return None, "requests package is not installed."

    url = f"{settings.llm_base_url}/api/generate"

    from app.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

    prompt = USER_PROMPT_TEMPLATE.format(
    context_json=json.dumps(context, ensure_ascii=False)
    )

    payload = {
    "model": settings.llm_model_name,
    "prompt": f"{SYSTEM_PROMPT.strip()}\n\n{prompt.strip()}",
    "stream": False,
    "format": "json",
    }

    try:
        response = requests.post(url, json=payload, timeout=settings.llm_timeout_seconds)
        response.raise_for_status()
        data = response.json()

        raw_text = data.get("response", "").strip()
        if not raw_text:
            return None, "Empty response from local model."

        parsed_json = json.loads(raw_text)
        validated = LLMReportSchema.model_validate(parsed_json)

        return (
            LLMReport(
            summary=validated.summary,
            top_issues=validated.top_issues,
            overall_assessment=validated.overall_assessment,
            recommended_actions=validated.recommended_actions,
            ),
            None,
            )
    except Exception as e:
        return None, str(e)

def generate_llm_report(
    profile: DatasetProfile,
    findings: list[Finding],
    quality: QualityScoreResult,
    ) -> tuple[LLMReport, LLMExecutionInfo]:
    if not settings.llm_enabled:
        fallback = _build_fallback_report(profile, findings, quality)
        return fallback, LLMExecutionInfo(
            enabled=False,
            mode="disabled",
            used_fallback=True,
            model_name=None,
            call_count=0,
            success=True,
            error_message=None,
            )

    context = build_llm_context(profile, findings, quality)

    if settings.llm_mode == "ollama":
        report, error = _call_ollama_once(context)
        if report is not None:
            return report, LLMExecutionInfo(
                    enabled=True,
                    mode="ollama",
                    used_fallback=False,
                    model_name=settings.llm_model_name,
                    call_count=1,
                    success=True,
                    error_message=None,
                )

        fallback = _build_fallback_report(profile, findings, quality)
        return fallback, LLMExecutionInfo(
            enabled=True,
            mode="ollama",
            used_fallback=True,
            model_name=settings.llm_model_name,
            call_count=1,
            success=False,
            error_message=error,
            )

    fallback = _build_fallback_report(profile, findings, quality)
    return fallback, LLMExecutionInfo(
        enabled=True,
        mode="fallback",
        used_fallback=True,
        model_name=None,
        call_count=0,
        success=True,
        error_message=None,
        )