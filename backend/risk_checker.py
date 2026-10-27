
def check_risks(dataset_report=None, evaluation_report=None):
    risks = []

    if dataset_report is not None:
        missing_values = dataset_report.get("missing_values", {})
        duplicate_rows = dataset_report.get("duplicate_rows", 0)

        for column, count in missing_values.items():
            if count > 0:
                risks.append({
                    "category": "Data Quality",
                    "severity": "Medium",
                    "issue": (
                        f"Column '{column}' contains "
                        f"{count} missing value(s)."
                    ),
                    "recommendation": (
                        "Investigate the missing data and choose "
                        "an appropriate handling strategy."
                    )
                })

        if duplicate_rows > 0:
            risks.append({
                "category": "Data Quality",
                "severity": "Low",
                "issue": (
                    f"The dataset contains {duplicate_rows} "
                    "duplicate row(s)."
                ),
                "recommendation": (
                    "Check whether these rows are genuine duplicates "
                    "before removing them."
                )
            })

    if evaluation_report is not None:
        thresholds = {
            "accuracy": 0.80,
            "precision": 0.80,
            "recall": 0.80,
            "f1_score": 0.80,
        }

        for metric, threshold in thresholds.items():
            value = evaluation_report.get(metric)

            if value is None:
                continue

            if value < threshold:
                risks.append({
                    "category": "Model Performance",
                    "severity": "Medium",
                    "issue": (
                        f"{metric.replace('_', ' ').title()} "
                        f"is {value:.2%}, below the "
                        f"{threshold:.0%} review threshold."
                    ),
                    "recommendation": (
                        "Review model performance and determine "
                        "whether further evaluation is required."
                    )
                })

    return {
        "risk_count": len(risks),
        "risks": risks,
        "note": (
            "Preliminary automated checks only. "
            "These results do not establish fairness, safety, "
            "or regulatory compliance."
        )
    }
