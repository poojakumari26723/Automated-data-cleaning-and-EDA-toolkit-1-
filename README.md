# P-15: Automated Data Cleaning and EDA Toolkit

A beginner-friendly Python project that loads a CSV or Excel dataset, fills missing values, removes duplicate rows, detects outliers, creates summary statistics and charts, and exports a cleaned CSV plus an HTML report.

## 1. Project structure

```text
P15_EDA_Toolkit/
├── main.py
├── README.md
├── datasets/
│   └── dataset1.csv
└── output/
    └── .gitkeep
```

The `output` folder will contain generated results after you run the program.

## 2. Requirements

- Python 3.9 or newer recommended
- Visual Studio Code (optional, but beginner-friendly)

## 3. Install the libraries

Open the project folder in VS Code. Select **Terminal → New Terminal**, then run:

```bash
python -m pip install pandas numpy matplotlib seaborn openpyxl
```

If `python` is not recognized on Windows, try:

```bash
py -m pip install pandas numpy matplotlib seaborn openpyxl
```

## 4. Run the project

Make sure the terminal is in the `P15_EDA_Toolkit` project folder. Run:

```bash
python main.py
```

Or, on Windows if needed:

```bash
py main.py
```

The project starts with the included sample file `datasets/dataset1.csv`.

## 5. Output files

After a successful run, open the `output` folder. It should contain:

- `cleaned_data.csv` — dataset after filling missing values and removing exact duplicate rows
- `eda_report.html` — report with dataset details, summaries, outlier counts, and charts
- `histogram_*.png` — histograms for numerical columns
- `boxplot_*.png` — box plots for numerical columns
- `correlation_heatmap.png` — created when the dataset has at least two numerical columns

To view the report, double-click `output/eda_report.html` or open it in your web browser.

## 6. Use a different dataset

Place your CSV file in the `datasets` folder and run, for example:

```bash
python main.py datasets/my_data.csv
```

Excel files are also supported:

```bash
python main.py datasets/my_data.xlsx
```

The file must exist and have a `.csv`, `.xlsx`, or `.xls` extension. For Excel files, the `openpyxl` package is installed above.

## 7. Outlier detection

The default method is IQR. In `main.py`, find:

```python
outlier_method = "iqr"
```

Change it to:

```python
outlier_method = "zscore"
```

to use Z-score detection (threshold: absolute Z-score greater than 3). The program reports outliers but does not delete them, because an extreme value may be genuine.

## 8. What the project demonstrates

- **NumPy:** numeric data handling and calculations
- **Classes and objects:** `DataCleaningToolkit` class
- **Pandas:** reading, validating, cleaning, and summarizing data
- **Data visualization:** histograms, box plots, and correlation heatmaps
- **Report export:** cleaned CSV and HTML EDA report

## 9. Test on three datasets

For the assignment's three-dataset requirement, test the program with three different files, for example:

1. Student performance dataset
2. Sales dataset
3. Employee dataset

Save each file under `datasets/` and run it using the command shown in section 6. Save screenshots or notes of each successful run for your submission.

## Notes

- Missing numerical values are filled with the column median.
- Missing categorical values are filled with the mode; all-missing categorical columns use `Unknown`.
- Exact duplicate rows are removed.
- Outliers are detected but not automatically removed.
- The output files may be overwritten each time you run the program, so copy or rename results if you need to preserve results from separate datasets.
