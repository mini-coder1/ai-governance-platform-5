
import pandas as pd
import pytest
from data_analyzer import analyze_dataset


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "study_hours": [2, 4, 6, 3, 5],
        "attendance": [60, 80, 95, 70, None],
        "result": ["Fail", "Pass", "Pass", "Fail", "Pass"]
    })


def test_analyze_dataset_reports_row_and_column_counts(sample_dataframe):
    report = analyze_dataset(sample_dataframe)

    assert report["rows"] == 5
    assert report["columns"] == 3


def test_analyze_dataset_detects_missing_values(sample_dataframe):
    report = analyze_dataset(sample_dataframe)

    assert report["missing_values"]["attendance"] == 1
    assert report["missing_values"]["study_hours"] == 0


def test_analyze_dataset_reports_column_names(sample_dataframe):
    report = analyze_dataset(sample_dataframe)

    assert report["column_names"] == [
        "study_hours", "attendance", "result"
    ]


def test_analyze_dataset_reports_duplicate_rows(sample_dataframe):
    report = analyze_dataset(sample_dataframe)

    assert report["duplicate_rows"] == 0


def test_analyze_dataset_rejects_empty_dataframe():
    with pytest.raises(ValueError):
        analyze_dataset(pd.DataFrame())
