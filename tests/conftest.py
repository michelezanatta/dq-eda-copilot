import io

import pandas as pd
import pytest

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "id": ["A1", "A2", "A3", "A4"],
            "age": [25, 30, None, 45],
            "salary": [1000.0, 1200.0, 1300.0, 99999.0],
            "country": ["IT", "IT", "DE", None],
            "is_active": ["yes", "no", "yes", "yes"],
            "signup_date": ["2024-01-01", "2024-01-02", None, "2024-01-10"],
            "notes": [
                "short text",
                "this is a somewhat longer free text field",
                "another long free text field for testing",
                None,
            ],
        }
    )

@pytest.fixture
def sample_csv_bytes(sample_dataframe):
    buffer = io.StringIO()
    sample_dataframe.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")

@pytest.fixture
def sample_parquet_bytes(sample_dataframe):
    buffer = io.BytesIO()
    sample_dataframe.to_parquet(buffer, index=False)
    return buffer.getvalue()