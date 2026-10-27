
import pytest
from model_evaluator import evaluate_model


def test_evaluate_model_returns_metrics():
    actual = ["Pass", "Pass", "Fail", "Fail", "Pass"]
    predicted = ["Pass", "Fail", "Fail", "Fail", "Pass"]

    report = evaluate_model(actual, predicted)

    assert report["accuracy"] == 0.8
    assert report["precision"] == 0.8667
    assert report["recall"] == 0.8
    assert report["f1_score"] == 0.8
    assert "confusion_matrix" in report


def test_evaluate_model_rejects_empty_actual_labels():
    with pytest.raises(ValueError, match="Actual labels cannot be empty"):
        evaluate_model([], [])


def test_evaluate_model_rejects_different_lengths():
    with pytest.raises(ValueError, match="same length"):
        evaluate_model(["Pass", "Fail"], ["Pass"])


def test_evaluate_model_rejects_missing_labels():
    with pytest.raises(ValueError, match="cannot contain missing values"):
        evaluate_model(["Pass", None], ["Pass", "Fail"])
