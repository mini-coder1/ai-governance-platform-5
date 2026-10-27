
import json
import pytest
from report_generator import (
    generate_governance_report,
    save_report,
    generate_pdf_report,
    generate_model_card,
    generate_model_card_pdf
)


@pytest.fixture
def sample_reports():
    dataset_report = {
        "rows": 5,
        "columns": 2,
        "column_names": ["actual", "predicted"],
        "missing_values": {"actual": 0, "predicted": 0},
        "duplicate_rows": 2
    }

    evaluation_report = {
        "accuracy": 0.80,
        "precision": 0.8667,
        "recall": 0.80,
        "f1_score": 0.80,
        "confusion_matrix": [[2, 0], [1, 2]]
    }

    risk_report = {
        "risk_count": 1,
        "risks": [
            {
                "category": "Data Quality",
                "severity": "Low",
                "issue": "The dataset contains 2 duplicate rows.",
                "recommendation": "Check whether these rows are genuine duplicates."
            }
        ]
    }

    return dataset_report, evaluation_report, risk_report


def test_governance_report_contains_expected_sections(sample_reports):
    dataset, evaluation, risks = sample_reports

    report = generate_governance_report(dataset, evaluation, risks)

    assert report["report_title"] == "AI Governance Report"
    assert report["dataset_analysis"] == dataset
    assert report["model_evaluation"] == evaluation
    assert report["risk_assessment"] == risks
    assert len(report["limitations"]) > 0
    assert "generated_at" in report


def test_save_report_creates_valid_json(tmp_path, sample_reports):
    dataset, evaluation, risks = sample_reports
    report = generate_governance_report(dataset, evaluation, risks)
    output_file = tmp_path / "governance_report.json"

    save_report(report, output_file)

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report["report_title"] == "AI Governance Report"
    assert saved_report["model_evaluation"]["accuracy"] == 0.80


def test_generate_pdf_report_creates_nonempty_pdf(tmp_path, sample_reports):
    dataset, evaluation, risks = sample_reports
    report = generate_governance_report(dataset, evaluation, risks)
    output_file = tmp_path / "governance_report.pdf"

    generate_pdf_report(report, str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    with open(output_file, "rb") as file:
        assert file.read(4) == b"%PDF"


def test_model_card_includes_custom_model_information(sample_reports):
    dataset, evaluation, risks = sample_reports

    model_info = {
        "model_name": "Student Performance Predictor",
        "purpose": "Predict student performance",
        "version": "2.0",
        "intended_use": "Educational planning",
        "model_type": "Random Forest Classifier",
        "training_data": "Historical student data",
        "limitations": "Requires representative training data"
    }

    card = generate_model_card(
        dataset, evaluation, risks, model_info
    )

    assert card["model_name"] == "Student Performance Predictor"
    assert card["version"] == "2.0"
    assert card["overview"]["purpose"] == "Predict student performance"
    assert card["overview"]["intended_use"] == "Educational planning"
    assert card["overview"]["model_type"] == "Random Forest Classifier"
    assert card["overview"]["training_data"] == "Historical student data"
    assert card["limitations"][0] == "Requires representative training data"
    assert card["dataset_summary"]["rows"] == 5
    assert card["evaluation_results"]["accuracy"] == 0.80


def test_model_card_uses_defaults_when_custom_info_is_missing():
    card = generate_model_card()

    assert card["model_name"] == "Model Under Evaluation"
    assert card["version"] == "Not specified"
    assert "overview" in card
    assert "limitations" in card


def test_generate_model_card_pdf_creates_nonempty_pdf(
    tmp_path, sample_reports
):
    dataset, evaluation, risks = sample_reports

    card = generate_model_card(
        dataset,
        evaluation,
        risks,
        {
            "model_name": "Test Model",
            "purpose": "Testing PDF generation",
            "version": "1.0"
        }
    )

    output_file = tmp_path / "model_card.pdf"

    generate_model_card_pdf(card, str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    with open(output_file, "rb") as file:
        assert file.read(4) == b"%PDF"
