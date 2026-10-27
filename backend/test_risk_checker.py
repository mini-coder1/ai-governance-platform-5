
import pytest
from risk_checker import check_risks


def test_detects_missing_values():
    dataset_report = {
        "missing_values": {
            "study_hours": 0,
            "attendance": 1,
            "result": 0
        },
        "duplicate_rows": 0
    }

    report = check_risks(dataset_report, None)

    assert report["risk_count"] == 1
    assert report["risks"][0]["category"] == "Data Quality"
    assert report["risks"][0]["severity"] == "Medium"
    assert "attendance" in report["risks"][0]["issue"]


def test_detects_duplicate_rows():
    dataset_report = {
        "missing_values": {},
        "duplicate_rows": 3
    }

    report = check_risks(dataset_report, None)

    assert report["risk_count"] == 1
    assert report["risks"][0]["severity"] == "Low"
    assert "3 duplicate row(s)" in report["risks"][0]["issue"]


def test_detects_low_model_metrics():
    evaluation_report = {
        "accuracy": 0.70,
        "precision": 0.90,
        "recall": 0.65,
        "f1_score": 0.75
    }

    report = check_risks(None, evaluation_report)

    assert report["risk_count"] == 3

    issues = [risk["issue"] for risk in report["risks"]]

    assert any("Accuracy" in issue for issue in issues)
    assert any("Recall" in issue for issue in issues)
    assert any("F1 Score" in issue for issue in issues)


def test_metrics_at_threshold_do_not_trigger_risks():
    evaluation_report = {
        "accuracy": 0.80,
        "precision": 0.80,
        "recall": 0.80,
        "f1_score": 0.80
    }

    report = check_risks(None, evaluation_report)

    assert report["risk_count"] == 0
    assert report["risks"] == []


def test_no_risks_for_clean_dataset_and_good_metrics():
    dataset_report = {
        "missing_values": {
            "study_hours": 0,
            "attendance": 0,
            "result": 0
        },
        "duplicate_rows": 0
    }

    evaluation_report = {
        "accuracy": 0.90,
        "precision": 0.90,
        "recall": 0.90,
        "f1_score": 0.90
    }

    report = check_risks(dataset_report, evaluation_report)

    assert report["risk_count"] == 0
    assert report["risks"] == []


def test_report_contains_compliance_limitation_note():
    report = check_risks()

    assert report["risk_count"] == 0
    assert report["risks"] == []
    assert "fairness" in report["note"]
    assert "safety" in report["note"]
    assert "regulatory compliance" in report["note"]
