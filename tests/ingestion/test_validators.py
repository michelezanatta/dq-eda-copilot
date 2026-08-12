import pytest

from app.ingestion.validators import (
    IngestionValidationError,
    detect_format,
    validate_dataframe_shape,
    validate_filename,
    validate_memory_usage,
    validate_size,
)

def test_detect_format_csv():
    assert detect_format("file.csv") == "csv"

def test_detect_format_parquet():
    assert detect_format("file.parquet") == "parquet"

def test_detect_format_invalid():
    with pytest.raises(IngestionValidationError):
        detect_format("file.xlsx")

def test_validate_filename_ok():
    validate_filename("dataset.csv")

def test_validate_filename_empty():
    with pytest.raises(IngestionValidationError):
        validate_filename("")

def test_validate_size_ok():
    validate_size(100, 1000)

def test_validate_size_empty():
    with pytest.raises(IngestionValidationError):
        validate_size(0, 1000)

def test_validate_size_too_large():
    with pytest.raises(IngestionValidationError):
        validate_size(2000, 1000)

def test_validate_dataframe_shape_ok():
    validate_dataframe_shape(100, 10, 1000, 100)

def test_validate_dataframe_shape_too_many_rows():
    with pytest.raises(IngestionValidationError):
        validate_dataframe_shape(1001, 10, 1000, 100)

def test_validate_dataframe_shape_too_many_columns():
    with pytest.raises(IngestionValidationError):
        validate_dataframe_shape(100, 101, 1000, 100)

def test_validate_memory_usage_ok():
    validate_memory_usage(1024, 2048)

def test_validate_memory_usage_too_high():
    with pytest.raises(IngestionValidationError):
        validate_memory_usage(4096, 2048)