import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
from io import BytesIO

sns.set_style("whitegrid")


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding"""
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return img_str


def generate_eda_report(csv_path, output_path, title):
    print(f'Generating report: {title}')
    df = pd.read_csv(csv_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Basic Info
    shape_info = f"<h3>Dataset Shape:</h3> Rows: {df.shape[0]} | Columns: {df.shape[1]}"
    summary_stats = df.describe(include='all').to_html()

    # Missing Values
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    missing_html = missing.to_frame("Missing Count").to_html()

    # Correlation Heatmap (numeric only)
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    if numeric_df.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(numeric_df.corr(), cmap='coolwarm', ax=ax)
        heatmap_img = fig_to_base64(fig)
        heatmap_html = f'<h3>Correlation Heatmap</h3><img src="data:image/png;base64,{heatmap_img}"/>'
    else:
        heatmap_html = "<p>Not enough numeric columns for correlation heatmap.</p>"

    # Target Distribution (if TARGET exists)
    if "TARGET" in df.columns:
        fig, ax = plt.subplots()
        df["TARGET"].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Target Distribution")
        target_img = fig_to_base64(fig)
        target_html = f'<h3>Target Distribution</h3><img src="data:image/png;base64,{target_img}"/>'
    else:
        target_html = "<p>No TARGET column found.</p>"

    # Build HTML
    html_content = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; }}
            table, th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {shape_info}
        <h3>Summary Statistics</h3>
        {summary_stats}
        <h3>Missing Values</h3>
        {missing_html}
        {target_html}
        {heatmap_html}
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f'Saved to {output_path}')


if __name__ == '__main__':
    generate_eda_report(
        '../data/raw/application_train.csv',
        'reports/eda_credit_risk.html',
        'Credit Risk Application EDA'
    )

    generate_eda_report(
        '../data/raw/train_transaction.csv',
        'reports/eda_fraud.html',
        'Fraud Detection Transaction EDA'
    )