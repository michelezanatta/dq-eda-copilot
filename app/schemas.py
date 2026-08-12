from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    filename: str
    file_format: Literal["csv", "parquet"]
    size_bytes: int

class IngestionResult(BaseModel):
    metadata: FileMetadata
    row_count: int
    column_count: int
    columns: List[str]

class BaseColumnProfile(BaseModel):
    profile_type: str
    column: str
    dtype: str

    non_null_count: int
    null_count: int
    null_ratio: float

    unique_count: int
    unique_ratio: float
    is_constant: bool

    inferred_logical_type: str
    warnings: List[str] = Field(default_factory=list)

class NumericColumnProfile(BaseColumnProfile):
    profile_type: Literal["numeric"] = "numeric"

    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    p25: Optional[float] = None
    median: Optional[float] = None
    p75: Optional[float] = None
    max: Optional[float] = None
    iqr: Optional[float] = None

    outlier_count_iqr: Optional[int] = None
    outlier_ratio_iqr: Optional[float] = None

    zero_count: Optional[int] = None
    zero_ratio: Optional[float] = None

class CategoricalColumnProfile(BaseColumnProfile):
    profile_type: Literal["categorical"] = "categorical"

    top_values: List[Dict[str, Any]] = Field(default_factory=list)
    avg_length: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    is_boolean_like: bool = False
    is_id_like: bool = False
    is_free_text_like: bool = False

class DatetimeColumnProfile(BaseColumnProfile):
    profile_type: Literal["datetime"] = "datetime"

    min_date: Optional[str] = None
    max_date: Optional[str] = None
    range_days: Optional[int] = None

class BooleanColumnProfile(BaseColumnProfile):
    profile_type: Literal["boolean"] = "boolean"

    true_count: int = 0
    false_count: int = 0
    true_ratio: float = 0.0
    false_ratio: float = 0.0

class GenericColumnProfile(BaseColumnProfile):
    profile_type: Literal["other"] = "other"

ColumnProfile = Union[
    NumericColumnProfile,
    CategoricalColumnProfile,
    DatetimeColumnProfile,
    BooleanColumnProfile,
    GenericColumnProfile,
    ]

class DatasetProfile(BaseModel):
    row_count: int
    column_count: int
    total_cells: int
    total_missing_cells: int
    missing_cell_ratio: float

    duplicate_row_count: int
    duplicate_row_ratio: float

    memory_usage_bytes: int

    columns_by_type: Dict[str, int]

    constant_columns: List[str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    boolean_columns: List[str]
    other_columns: List[str]

    column_profiles: List[ColumnProfile]

    correlations: List[Dict[str, Any]] = Field(default_factory=list)

    truncated_correlations: bool = False
    profiling_warnings: List[str] = Field(default_factory=list)

class Finding(BaseModel):
    finding_type: str
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    message: str
    column: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    recommendation: Optional[str] = None
    rank_score: float = 0.0

class QualityScoreResult(BaseModel):
    quality_score: float
    quality_status: Literal["good", "fair", "poor"]
    severity_counts: Dict[str, int]
    total_findings: int
    penalties: Dict[str, float] = Field(default_factory=dict)

class LLMReport(BaseModel):
    summary: str
    top_issues: List[str] = Field(default_factory=list)
    overall_assessment: str
    recommended_actions: List[str] = Field(default_factory=list)

class LLMExecutionInfo(BaseModel):
    enabled: bool
    mode: str
    used_fallback: bool
    model_name: Optional[str] = None
    call_count: int = 0
    success: bool = False
    error_message: Optional[str] = None

class AnalysisResult(BaseModel):
    ingestion: IngestionResult
    profile: DatasetProfile
    findings: List[Finding]
    quality: QualityScoreResult
    llm_report: LLMReport
    llm_execution: LLMExecutionInfo

class AnalyzeResponse(AnalysisResult):
    pass