from pydantic import BaseModel, Field

class Settings(BaseModel):
    max_upload_size_bytes: int = 50 * 1024 * 1024
    max_rows: int = 2_000_000
    max_columns: int = 2_000
    max_memory_bytes_estimate: int = 512 * 1024 * 1024

    csv_encodings_to_try: list[str] = Field(
    default_factory=lambda: ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    )
    csv_separators_to_try: list[str] = Field(
    default_factory=lambda: [",", ";", "\t", "|"]
    )
    csv_bad_lines: str = "skip"

    max_top_values: int = 10

    datetime_detection_threshold: float = 0.80
    numeric_like_detection_threshold: float = 0.90
    boolean_like_detection_threshold: float = 0.95

    id_uniqueness_ratio_threshold: float = 0.98
    free_text_avg_length_threshold: float = 40.0
    free_text_uniqueness_ratio_threshold: float = 0.70

    correlation_method: str = "pearson"
    correlation_min_abs_threshold: float = 0.70
    max_columns_for_full_correlation: int = 50
    max_numeric_columns_in_correlation_output: int = 100
    max_correlation_pairs: int = 100

    profiling_sample_rows_for_wide_datasets: int = 100_000

    finding_missingness_medium: float = 0.05
    finding_missingness_high: float = 0.20
    finding_missingness_critical: float = 0.50

    finding_duplicate_rows_medium: float = 0.01
    finding_duplicate_rows_high: float = 0.05
    finding_duplicate_rows_critical: float = 0.20

    finding_outlier_ratio_medium: float = 0.01
    finding_outlier_ratio_high: float = 0.05
    finding_outlier_ratio_critical: float = 0.15

    finding_high_cardinality_ratio: float = 0.90
    finding_near_constant_ratio: float = 0.98

    finding_strong_correlation_high: float = 0.85
    finding_strong_correlation_critical: float = 0.95

    quality_penalty_low: float = 2.0
    quality_penalty_medium: float = 5.0
    quality_penalty_high: float = 10.0
    quality_penalty_critical: float = 20.0

    quality_status_good_min: float = 80.0
    quality_status_fair_min: float = 60.0

    llm_enabled: bool = True
    llm_mode : str = "fallback" # "ollama" # ["fallback", "ollama"]
    llm_base_url: str = "http://localhost:11434"
    llm_model_name: str = "llama3.2:latest"
    llm_timeout_seconds: int = 60
    llm_max_top_findings: int = 10

    request_logging_enabled: bool = True
    request_log_path: str = "logs/request_events.jsonl"

    cors_allowed_origins: list[str] = Field(
    default_factory=lambda: [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://michelezanatta.github.io",
    ]
    )


    datetime_formats_to_try: list[str] = Field(
                            default_factory=lambda: [
                            "%Y-%m-%d",
                            "%Y/%m/%d",
                            "%d/%m/%Y",
                            "%m/%d/%Y",
                            "%Y-%m-%d %H:%M:%S",
                            "%Y/%m/%d %H:%M:%S",
                            "%d/%m/%Y %H:%M:%S",
                            "%m/%d/%Y %H:%M:%S",
                            "%Y-%m-%dT%H:%M:%S",
                            "%Y-%m-%dT%H:%M:%S.%f",
                            ]
                            )

settings = Settings()



