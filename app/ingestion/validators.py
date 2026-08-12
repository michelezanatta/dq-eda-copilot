from pathlib import Path

SUPPORTED_EXTENSIONS = {".csv", ".parquet"}

class IngestionValidationError(ValueError):
    pass

def detect_format(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise IngestionValidationError(
            f"Unsupported file extension '{ext}'. Supported: .csv, .parquet"
        )
    return ext.replace(".", "")

def validate_filename(filename: str) -> None:
    if not filename or not filename.strip():
        raise IngestionValidationError("Filename is empty.")

def validate_size(size_bytes: int, max_size_bytes: int) -> None:
    if size_bytes <= 0:
        raise IngestionValidationError("Uploaded file is empty.")
    if size_bytes > max_size_bytes:
        raise IngestionValidationError(
            f"File too large: {size_bytes} bytes. Max allowed: {max_size_bytes} bytes."
        )

def validate_dataframe_shape(row_count: int, column_count: int, max_rows: int, max_columns: int) -> None:
    if row_count > max_rows:
        raise IngestionValidationError(
            f"Dataset has too many rows: {row_count}. Max allowed: {max_rows}."
        )

    if column_count > max_columns:
        raise IngestionValidationError(
            f"Dataset has too many columns: {column_count}. Max allowed: {max_columns}."
        )

def validate_memory_usage(memory_usage_bytes: int, max_memory_bytes_estimate: int) -> None:
    if memory_usage_bytes > max_memory_bytes_estimate:
        raise IngestionValidationError(
            f"Dataset estimated memory usage is too high: {memory_usage_bytes} bytes. "
            f"Max allowed: {max_memory_bytes_estimate} bytes."
        )