
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# Sample CSV files used by the tests
DATASET_CSV = (
    b"study_hours,attendance,result\n"
    b"2,80,Pass\n"
    b"4,90,Pass\n"
    b"1,,Fail\n"
)

EVALUATION_CSV = (
    b"actual,predicted\n"
    b"Pass,Pass\n"
    b"Fail,Fail\n"
    b"Pass,Fail\n"
    b"Fail,Fail\n"
)


def upload_csv(content, filename="sample.csv"):
    return {
        "file": (filename, BytesIO(content), "text/csv")
    }


# 1. Home endpoint
def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Governance Platform is running!"
    )


# 2. Dataset analysis
def test_analyze_dataset_success():
    response = client.post(
        "/analyze-dataset",
        files=upload_csv(DATASET_CSV)
    )

    assert response.status_code == 200

    body = response.json()
    assert body["filename"] == "sample.csv"
    assert body["analysis"]["rows"] == 3
    assert body["analysis"]["columns"] == 3
    assert body["analysis"]["missing_values"]["attendance"] == 1


def test_analyze_dataset_rejects_non_csv():
    response = client.post(
        "/analyze-dataset",
        files=upload_csv(b"hello", "sample.txt")
    )

    assert response.status_code == 400


def test_analyze_dataset_rejects_empty_file():
    response = client.post(
        "/analyze-dataset",
        files=upload_csv(b"")
    )

    assert response.status_code == 400


def test_analyze_dataset_rejects_missing_column_header():
    response = client.post(
        "/analyze-dataset",
        files=upload_csv(b"\n1,2\n3,4\n")
    )

    assert response.status_code == 400


# 3. Model evaluation
def test_evaluate_model_success():
    response = client.post(
        "/evaluate-model",
        files=upload_csv(EVALUATION_CSV, "evaluation.csv")
    )

    assert response.status_code == 200

    body = response.json()
    assert body["filename"] == "evaluation.csv"
    assert "accuracy" in body["evaluation"]


def test_evaluate_model_rejects_missing_required_columns():
    response = client.post(
        "/evaluate-model",
        files=upload_csv(b"name,score\nAlice,90\n")
    )

    assert response.status_code == 400


def test_evaluate_model_rejects_missing_labels():
    response = client.post(
        "/evaluate-model",
        files=upload_csv(
            b"actual,predicted\nPass,\n"
        )
    )

    assert response.status_code == 400


# 4. Risk checking
def test_check_risks():
    response = client.post(
        "/check-risks",
        json={
            "dataset_report": {
                "rows": 3,
                "columns": 3,
                "missing_values": {
                    "attendance": 1
                },
                "duplicate_rows": 0
            },
            "evaluation_report": {
                "accuracy": 0.9,
                "precision": 0.9,
                "recall": 0.9,
                "f1_score": 0.9
            }
        }
    )

    assert response.status_code == 200
    assert response.json() is not None


# 5. Governance JSON report
def test_generate_governance_report():
    response = client.post(
        "/generate-report",
        json={
            "dataset_report": {
                "rows": 3,
                "columns": 3,
                "column_names": [
                    "study_hours",
                    "attendance",
                    "result"
                ],
                "missing_values": {
                    "attendance": 1
                },
                "duplicate_rows": 0
            },
            "evaluation_report": {
                "accuracy": 0.9
            },
            "risk_report": {}
        }
    )

    assert response.status_code == 200
    assert response.json() is not None


# 6. Governance PDF report
def test_generate_governance_pdf():
    response = client.post(
        "/generate-pdf-report",
        json={}
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/pdf"
    )
    assert response.content.startswith(b"%PDF")


# 7. Model Card JSON
def test_generate_model_card():
    response = client.post(
        "/generate-model-card",
        json={
            "model_info": {
                "model_name": "Test Model",
                "purpose": "Testing",
                "version": "1.0",
                "intended_use": "Testing API responses",
                "model_type": "Classifier",
                "training_data": "Sample dataset",
                "limitations": "Limited test data"
            }
        }
    )

    assert response.status_code == 200
    assert response.json() is not None


# 8. Model Card PDF
def test_generate_model_card_pdf():
    response = client.post(
        "/generate-model-card-pdf",
        json={
            "model_info": {
                "model_name": "Test Model",
                "purpose": "Testing",
                "version": "1.0"
            }
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/pdf"
    )
    assert response.content.startswith(b"%PDF")
