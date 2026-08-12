from __future__ import annotations

from io import BytesIO
from typing import Tuple

import pandas as pd

from app.config import settings
from app.ingestion.validators import (
    detect_format,
    validate_dataframe_shape,
    validate_filename,
    validate_memory_usage,
    validate_size,
)
from app.schemas import FileMetadata, IngestionResult

def _try_load_csv(content: bytes) -> pd.DataFrame:
    last_error = None

    for encoding in settings.csv_encodings_to_try:
        try:
            df = pd.read_csv(
                BytesIO(content),
                sep=None,
                engine="python",
                encoding=encoding,
                on_bad_lines=settings.csv_bad_lines,
            )
            return df
        except Exception as e:
            last_error = e

    for encoding in settings.csv_encodings_to_try:
        for sep in settings.csv_separators_to_try:
            try:
                df = pd.read_csv(
                    BytesIO(content),
                    sep=sep,
                    engine="python",
                    encoding=encoding,
                    on_bad_lines=settings.csv_bad_lines,
                )
                return df
            except Exception as e:
                last_error = e

    raise ValueError(f"Unable to parse CSV with configured encodings/separators. Last error: {last_error}")

def load_dataframe_from_bytes(filename: str, content: bytes) -> Tuple[pd.DataFrame, IngestionResult]:
    validate_filename(filename)
    validate_size(len(content), settings.max_upload_size_bytes)

    file_format = detect_format(filename)

    if file_format == "csv":
        df = _try_load_csv(content)
    elif file_format == "parquet":
        df = pd.read_parquet(BytesIO(content))
    else:
        raise ValueError(f"Unsupported format: {file_format}")

    df.columns = [str(c) for c in df.columns]

    row_count = int(df.shape[0])
    column_count = int(df.shape[1])

    validate_dataframe_shape(
        row_count=row_count,
        column_count=column_count,
        max_rows=settings.max_rows,
        max_columns=settings.max_columns,
    )

    memory_usage_bytes = int(df.memory_usage(deep=True).sum())
    validate_memory_usage(
        memory_usage_bytes=memory_usage_bytes,
        max_memory_bytes_estimate=settings.max_memory_bytes_estimate,
    )

    metadata = FileMetadata(
        filename=filename,
        file_format=file_format,
        size_bytes=len(content),
    )

    ingestion_result = IngestionResult(
        metadata=metadata,
        row_count=row_count,
        column_count=column_count,
        columns=df.columns.tolist(),
    )

    return df, ingestion_result