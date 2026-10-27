
import pandas as pd


def analyze_dataset(df):
    if df.empty:
        raise ValueError("The dataset is empty.")

    missing_values = df.isnull().sum().to_dict()
    duplicate_rows = int(df.duplicated().sum())

    total_rows = len(df)

    missing_percentages = {}

    for column in df.columns:
        missing_count = int(missing_values[column])
        percentage = (missing_count / total_rows) * 100

        missing_percentages[column] = round(percentage, 2)

    warnings = []

    for column, count in missing_values.items():
        if count > 0:
            warnings.append(
                f"Column '{column}' has {count} missing value(s)."
            )

    if duplicate_rows > 0:
        warnings.append(
            f"The dataset contains {duplicate_rows} duplicate row(s)."
        )

    if not warnings:
        warnings.append("No basic data-quality issues detected.")

    report = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": missing_values,
        "missing_percentages": missing_percentages,
        "duplicate_rows": duplicate_rows,
        "warnings": warnings,
    }

    return report
