import pandas as pd

from app.profiling.type_inference import (
    detect_boolean_like,
    detect_datetime_like,
    detect_free_text_like,
    detect_id_like,
    detect_numeric_like,
    infer_logical_type,
)

def test_detect_boolean_like():
    s = pd.Series(["yes", "no", "yes", "no"])
    assert detect_boolean_like(s) is True

def test_detect_numeric_like():
    s = pd.Series(["10", "20", "30", None])
    assert detect_numeric_like(s) is True

def test_detect_datetime_like():
    s = pd.Series(["2024-01-01", "2024-02-01", None])
    assert detect_datetime_like(s) is True

def test_detect_id_like():
    s = pd.Series(["ID001", "ID002", "ID003", "ID004"])
    assert detect_id_like(s) is True

def test_detect_free_text_like():
    s = pd.Series(
        [
            "This is a long sentence for testing purposes",
            "Another descriptive sentence that should be considered free text",
            "Yet another free text sample with enough length",
        ]
    )
    assert detect_free_text_like(s) is True

def test_infer_logical_type_boolean():
    s = pd.Series(["true", "false", "true"])
    assert infer_logical_type(s) == "boolean"

def test_infer_logical_type_numeric():
    s = pd.Series(["1", "2", "3"])
    assert infer_logical_type(s) == "numeric"

def test_infer_logical_type_datetime():
    s = pd.Series(["2024-01-01", "2024-01-02"])
    assert infer_logical_type(s) == "datetime"