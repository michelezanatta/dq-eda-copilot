from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)

def test_analyze_csv(sample_csv_bytes):
    response = client.post(
    "/api/analyze",
    files={"file": ("dataset.csv", sample_csv_bytes, "text/csv")},
    )

    assert response.status_code == 200

    data = response.json()
    assert "ingestion" in data
    assert "profile" in data
    assert "findings" in data
    assert "quality" in data
    assert data["ingestion"]["metadata"]["file_format"] == "csv"
    assert data["profile"]["row_count"] == 4

def test_analyze_parquet(sample_parquet_bytes):
    response = client.post(
    "/api/analyze",
    files={"file": ("dataset.parquet", sample_parquet_bytes, "application/octet-stream")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ingestion"]["metadata"]["file_format"] == "parquet"
    assert "findings" in data
    assert "quality" in data

def test_analyze_invalid_extension():
    response = client.post(
    "/api/analyze",
    files={"file": ("dataset.xlsx", b"dummy", "application/octet-stream")},
    )

    assert response.status_code == 400

def test_analyze_empty_file():
    response = client.post(
    "/api/analyze",
    files={"file": ("dataset.csv", b"", "text/csv")},
    )

    assert response.status_code == 400

def test_analyze_html_report(sample_csv_bytes):
    response = client.post(
    "/api/analyze/report/html",
    files={"file": ("dataset.csv", sample_csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Data Quality Report" in response.text