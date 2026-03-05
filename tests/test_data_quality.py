import pandas as pd
import os


def validate_credit_risk_data():

    # Build absolute path safely
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(
        base_dir, "data", "raw", "application_train.csv"
    )

    df = pd.read_csv(csv_path)

    # -------------------------------
    # Column existence checks
    # -------------------------------
    required_columns = [
        'TARGET',
        'AMT_CREDIT',
        'AMT_INCOME_TOTAL',
        'SK_ID_CURR'
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # -------------------------------
    # Value range checks
    # -------------------------------
    if not df['TARGET'].between(0, 1).all():
        raise ValueError("TARGET must be 0 or 1")

    if not df['AMT_CREDIT'].between(0, 1e8).all():
        raise ValueError("Credit amount out of range")

    # -------------------------------
    # Not null checks
    # -------------------------------
    if df['SK_ID_CURR'].isnull().any():
        raise ValueError("Customer ID cannot be null")

    # -------------------------------
    # Default rate sanity check
    # -------------------------------
    default_rate = df['TARGET'].mean()

    if not (0.03 < default_rate < 0.25):
        raise ValueError(
            f"Unexpected default rate: {default_rate:.2%}"
        )

    print("All data quality checks passed!")
    return True


if __name__ == '__main__':
    validate_credit_risk_data()