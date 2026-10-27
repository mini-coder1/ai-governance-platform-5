
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

import pandas as pd


def evaluate_model(y_true, y_pred):
    if len(y_true) == 0:
        raise ValueError("Actual labels cannot be empty.")

    if len(y_true) != len(y_pred):
        raise ValueError(
            "Actual and predicted labels must have the same length."
        )

    actual = pd.Series(y_true)
    predicted = pd.Series(y_pred)

    if actual.isnull().any() or predicted.isnull().any():
        raise ValueError(
            "Actual and predicted labels cannot contain missing values."
        )

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(
        y_true, y_pred, average="weighted", zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, average="weighted", zero_division=0
    )
    f1 = f1_score(
        y_true, y_pred, average="weighted", zero_division=0
    )
    matrix = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": matrix,
    }
