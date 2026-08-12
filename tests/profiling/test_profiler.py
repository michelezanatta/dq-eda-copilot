from app.profiling.profiler import build_dataset_profile

def test_build_dataset_profile_basic(sample_dataframe):
    profile = build_dataset_profile(sample_dataframe)

    assert profile.row_count == 4
    assert profile.column_count == 7
    assert profile.total_cells == 28
    assert profile.total_missing_cells >= 1
    assert "age" in profile.numeric_columns
    assert "country" in profile.categorical_columns
    assert "signup_date" in profile.datetime_columns or "signup_date" in [p.column for p in profile.column_profiles]

def test_build_dataset_profile_has_column_profiles(sample_dataframe):
    profile = build_dataset_profile(sample_dataframe)

    assert len(profile.column_profiles) == sample_dataframe.shape[1]

def test_build_dataset_profile_boolean_detection(sample_dataframe):
    profile = build_dataset_profile(sample_dataframe)

    bool_profiles = [p for p in profile.column_profiles if p.column == "is_active"]
    assert len(bool_profiles) == 1
    assert bool_profiles[0].inferred_logical_type == "boolean"

def test_build_dataset_profile_constant_column():
    import pandas as pd

    df = pd.DataFrame(
        {
            "constant_col": ["A", "A", "A"],
            "value": [1, 2, 3],
        }
    )

    profile = build_dataset_profile(df)

    assert "constant_col" in profile.constant_columns

def test_build_dataset_profile_duplicate_rows():
    import pandas as pd

    df = pd.DataFrame(
        {
            "a": [1, 1, 2],
            "b": ["x", "x", "y"],
        }
    )

    profile = build_dataset_profile(df)

    assert profile.duplicate_row_count == 1

def test_build_dataset_profile_correlations():
    import pandas as pd

    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10],
            "z": [5, 4, 3, 2, 1],
        }
    )

    profile = build_dataset_profile(df)

    assert isinstance(profile.correlations, list)