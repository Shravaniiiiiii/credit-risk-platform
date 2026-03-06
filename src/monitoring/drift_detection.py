from evidently.report import Report
from evidently.presets import DataDriftPreset
import pandas as pd
import os

def run_drift_report(reference_path, current_path, output_path="reports/drift_report.html"):

    print("Loading datasets...")

    reference = pd.read_csv(reference_path).sample(5000, random_state=42)
    current   = pd.read_csv(current_path).sample(2000, random_state=99)

    # numeric columns
    num_cols = reference.select_dtypes(include="number").columns.tolist()
    num_cols = [c for c in num_cols if c != "TARGET"][:20]

    print("Running drift analysis...")

    report = Report(metrics=[
        DataDriftPreset()
    ])

    report.run(
        reference_data=reference[num_cols],
        current_data=current[num_cols]
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report.save_html(output_path)

    print(f"Drift report saved: {output_path}")


if __name__ == "__main__":

    print("Preparing reference and current datasets...")

    df = pd.read_csv("data/raw/application_train.csv")

    ref = df.iloc[:int(len(df)*0.8)]
    cur = df.iloc[int(len(df)*0.8):]

    os.makedirs("data/processed", exist_ok=True)

    ref.to_csv("data/processed/reference.csv", index=False)
    cur.to_csv("data/processed/current.csv", index=False)

    run_drift_report(
        "data/processed/reference.csv",
        "data/processed/current.csv",
        "reports/drift_report.html"
    )