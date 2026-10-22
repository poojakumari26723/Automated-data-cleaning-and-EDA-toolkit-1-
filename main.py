import os
import sys
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


class DataCleaningToolkit:
    """Load, clean, analyze, visualize, and report on a CSV or Excel dataset."""

    def __init__(self, file_path, output_dir="output", outlier_method="iqr"):
        self.file_path = file_path
        self.output_dir = output_dir
        self.outlier_method = outlier_method.lower()
        self.df = None
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """Load a CSV or Excel file and perform basic validation."""
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(
                f"Dataset not found: {self.file_path}\n"
                "Check the file path and make sure the dataset is in the datasets folder."
            )

        extension = os.path.splitext(self.file_path)[1].lower()
        if extension == ".csv":
            self.df = pd.read_csv(self.file_path)
        elif extension in (".xlsx", ".xls"):
            self.df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file type. Please use CSV, XLSX, or XLS.")

        if self.df.empty:
            raise ValueError("The dataset has no rows.")
        if len(self.df.columns) == 0:
            raise ValueError("The dataset has no columns.")
        if self.df.columns.duplicated().any():
            duplicates = self.df.columns[self.df.columns.duplicated()].tolist()
            raise ValueError(f"Duplicate column names found: {duplicates}")

        print("\nDataset loaded successfully!")
        print(f"Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}")
        print("\nFirst five rows:")
        print(self.df.head().to_string(index=False))

    def handle_missing_values(self):
        """Fill numeric missing values with the median and categorical with the mode."""
        missing_before = int(self.df.isna().sum().sum())
        print(f"\nMissing values before cleaning: {missing_before}")

        for column in self.df.columns:
            if not self.df[column].isna().any():
                continue

            if pd.api.types.is_numeric_dtype(self.df[column]):
                median = self.df[column].median()
                # An all-missing numeric column has no median.
                fill_value = median if pd.notna(median) else 0
                self.df[column] = self.df[column].fillna(fill_value)
            else:
                modes = self.df[column].mode(dropna=True)
                fill_value = modes.iloc[0] if not modes.empty else "Unknown"
                self.df[column] = self.df[column].fillna(fill_value)

        print(f"Missing values filled: {missing_before}")

    def remove_duplicates(self):
        """Remove exact duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates().copy()
        removed = before - len(self.df)
        print(f"Duplicate rows removed: {removed}")
        return removed

    def detect_outliers(self):
        """Detect outliers in numeric columns using IQR or Z-score; do not delete them."""
        numeric_columns = self.df.select_dtypes(include=np.number).columns
        results = {}

        for column in numeric_columns:
            values = self.df[column].dropna()
            if values.empty:
                results[column] = 0
                continue

            if self.outlier_method == "zscore":
                std = values.std(ddof=0)
                if std == 0 or pd.isna(std):
                    count = 0
                else:
                    z_scores = (self.df[column] - values.mean()) / std
                    count = int((z_scores.abs() > 3).sum())
            else:
                q1 = values.quantile(0.25)
                q3 = values.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                count = int(((self.df[column] < lower) |
                             (self.df[column] > upper)).sum())

            results[column] = count

        print(f"\nOutliers detected using {self.outlier_method.upper()}:")
        if results:
            for column, count in results.items():
                print(f"  {column}: {count}")
        else:
            print("  No numeric columns available.")
        return results

    def generate_statistics(self):
        """Create numeric and categorical summaries."""
        numeric = self.df.select_dtypes(include=np.number)
        categorical = self.df.select_dtypes(exclude=np.number)

        numeric_html = (
            numeric.describe().round(2).to_html(classes="data-table", border=0)
            if not numeric.empty else "<p>No numerical columns found.</p>"
        )
        categorical_html = (
            categorical.describe().to_html(classes="data-table", border=0)
            if not categorical.empty else "<p>No categorical columns found.</p>"
        )

        print("\nNumerical summary:")
        print(numeric.describe().round(2).to_string() if not numeric.empty else "No numeric columns.")
        print("\nCategorical summary:")
        print(categorical.describe().to_string() if not categorical.empty else "No categorical columns.")
        return numeric_html, categorical_html

    def generate_charts(self):
        """Save histograms, box plots, and (when possible) a correlation heatmap."""
        numeric_columns = self.df.select_dtypes(include=np.number).columns
        chart_files = []

        for column in numeric_columns:
            safe_name = "".join(
                char if char.isalnum() or char in ("-", "_") else "_"
                for char in str(column)
            )

            plt.figure(figsize=(7, 4))
            self.df[column].dropna().hist(bins=15)
            plt.title(f"Histogram: {column}")
            plt.xlabel(str(column))
            plt.ylabel("Frequency")
            plt.tight_layout()
            filename = f"histogram_{safe_name}.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=120)
            plt.close()
            chart_files.append(filename)

            plt.figure(figsize=(7, 4))
            sns.boxplot(x=self.df[column])
            plt.title(f"Box Plot: {column}")
            plt.tight_layout()
            filename = f"boxplot_{safe_name}.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=120)
            plt.close()
            chart_files.append(filename)

        if len(numeric_columns) >= 2:
            plt.figure(figsize=(max(6, len(numeric_columns)), 5))
            sns.heatmap(
                self.df[numeric_columns].corr(),
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                vmin=-1,
                vmax=1,
            )
            plt.title("Correlation Heatmap")
            plt.tight_layout()
            filename = "correlation_heatmap.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=120)
            plt.close()
            chart_files.append(filename)

        print(f"\nCharts saved: {len(chart_files)}")
        return chart_files

    def export_results(self, numeric_html, categorical_html, outliers, chart_files,
                       duplicates_removed, missing_before):
        """Export cleaned CSV and a self-contained HTML report with linked chart files."""
        cleaned_path = os.path.join(self.output_dir, "cleaned_data.csv")
        self.df.to_csv(cleaned_path, index=False)

        missing_table = self.df.isna().sum().rename("Missing values").to_frame().to_html(
            classes="data-table", border=0
        )
        outlier_rows = "".join(
            f"<tr><td>{column}</td><td>{count}</td></tr>"
            for column, count in outliers.items()
        )
        if not outlier_rows:
            outlier_rows = '<tr><td colspan="2">No numeric columns found.</td></tr>'

        chart_html = ""
        for filename in chart_files:
            chart_html += (
                f"<section><h3>{filename}</h3>"
                f'<img src="{filename}" alt="{filename}"></section>\n'
            )
        if not chart_html:
            chart_html = "<p>No charts could be generated for this dataset.</p>"

        report_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Automated Data Cleaning and EDA Report</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 30px auto; padding: 0 18px; color: #222; background: #f5f7fa; }}
header, section, .panel {{ background: white; padding: 20px; margin: 18px 0; border-radius: 10px; box-shadow: 0 1px 5px #0001; }}
h1, h2 {{ color: #243b55; }}
.data-table {{ border-collapse: collapse; width: 100%; margin: 12px 0; background: white; }}
.data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
.data-table th {{ background: #eaf0f6; }}
img {{ max-width: 100%; height: auto; }}
small {{ color: #555; }}
</style>
</head>
<body>
<header>
<h1>Automated Data Cleaning and EDA Report</h1>
<p>Generated by the P-15 Data Cleaning Toolkit.</p>
<p><b>Input file:</b> {os.path.basename(self.file_path)}</p>
<p><b>Rows after cleaning:</b> {len(self.df)} &nbsp; <b>Columns:</b> {len(self.df.columns)}</p>
</header>
<section><h2>Cleaning Summary</h2>
<ul>
<li>Missing values before cleaning: {missing_before}</li>
<li>Duplicate rows removed: {duplicates_removed}</li>
<li>Outlier detection method: {self.outlier_method.upper()}</li>
<li>Outliers are reported, not automatically removed.</li>
</ul>
<h3>Missing values after cleaning</h3>{missing_table}
</section>
<section><h2>Numerical Summary</h2>{numeric_html}</section>
<section><h2>Categorical Summary</h2>{categorical_html}</section>
<section><h2>Outlier Counts</h2>
<table class="data-table"><thead><tr><th>Column</th><th>Outliers detected</th></tr></thead>
<tbody>{outlier_rows}</tbody></table>
</section>
<section><h2>Visualizations</h2>{chart_html}</section>
<footer><small>Note: Review detected outliers before deciding whether to remove them. Some extreme values may be valid.</small></footer>
</body></html>"""

        report_path = os.path.join(self.output_dir, "eda_report.html")
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(report_html)

        print(f"\nCleaned dataset saved to: {cleaned_path}")
        print(f"HTML report saved to: {report_path}")

    def run(self):
        self.load_data()
        missing_before = int(self.df.isna().sum().sum())
        self.handle_missing_values()
        duplicates_removed = self.remove_duplicates()
        outliers = self.detect_outliers()
        numeric_html, categorical_html = self.generate_statistics()
        chart_files = self.generate_charts()
        self.export_results(
            numeric_html, categorical_html, outliers, chart_files,
            duplicates_removed, missing_before
        )
        print("\nToolkit completed successfully!")


def main():
    dataset_path = os.path.join("datasets", "dataset1.csv")
    output_path = "output"
    outlier_method = "iqr"  # Change to "zscore" to use Z-score detection.

    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]

    toolkit = DataCleaningToolkit(
        file_path=dataset_path,
        output_dir=output_path,
        outlier_method=outlier_method,
    )
    try:
        toolkit.run()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
