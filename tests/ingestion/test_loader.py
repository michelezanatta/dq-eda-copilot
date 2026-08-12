from app.ingestion.loader import load_dataframe_from_bytes

def test_load_csv(sample_csv_bytes):
    df, ingestion = load_dataframe_from_bytes("dataset.csv", sample_csv_bytes)

    assert df.shape[0] == 4
    assert ingestion.metadata.file_format == "csv"
    assert ingestion.row_count == 4
    assert ingestion.column_count == 7
    assert "age" in ingestion.columns

def test_load_parquet(sample_parquet_bytes):
    df, ingestion = load_dataframe_from_bytes("dataset.parquet", sample_parquet_bytes)

    assert df.shape[0] == 4
    assert ingestion.metadata.file_format == "parquet"
    assert ingestion.row_count == 4
    assert ingestion.column_count == 7

def test_load_csv_with_semicolon_separator():
    content = b"id;name;value\n1;Alice;10\n2;Bob;20\n"
    df, ingestion = load_dataframe_from_bytes("dataset.csv", content)

    assert ingestion.row_count == 2
    assert ingestion.column_count == 3
    assert df.columns.tolist() == ["id", "name", "value"]

def test_load_csv_skips_bad_lines():
    content = b"id,name,value\n1,Alice,10\n2,Bob,20,EXTRA\n3,Carol,30\n"
    df, ingestion = load_dataframe_from_bytes("dataset.csv", content)

    assert ingestion.row_count >= 2
    assert "id" in df.columns