# 📊 Big Data Cleaning (DuckDB & PySpark)

Utilities for checking and fixing data quality on large tabular datasets.
The same API can run either on DuckDB (local, up to ~100 GB) or on PySpark (cluster / very large data). 
This project started as a learning exercise in building practical data-quality checks with DuckDB and PySpark, but the code is intended to be usable in real projects as well.

## 🚀 Features

**Two main operations**
- `check_data(df, engine=...)`
  - Generates a JSON-like report describing the quality and basic characteristics of every column.
- `fix_data(df, engine=...)`
  - Applies cleaning rules to a DataFrame based on the issues detected in the check step.

- **Pluggable engines**
  - `engine="duckdb"` – run checks with DuckDB SQL (currently implemented).
  - `engine="spark"` – intended to run on PySpark for very large datasets (API stub exists, logic still to be implemented

- **Convenient report viewer**
  - `utils.show_struct.show_struct()` renders the JSON report as collapsible YAML/JSON in Jupyter so it’s easy to inspect column-level issues.

## ⚙️ Work in progress
- DuckDB check logic is implemented.
- Cleaning logic (fix_data) is currently a passthrough (returns the original DataFrame).
- The Spark engine has placeholder functions and will be expanded.

## 🌳 Project structure


```
bigdata_cleaning/
├─ bigdata_cleaning/
│  ├─ core.py                    ← generic cleaning logic
│  ├─ duckdb_engine.py           ← duckdb–specific helpers
│  └─ spark_engine.py            ← spark–specific helpers
├─ data/
│  └─ ...                        ← parquet files etc.
├─ scripts/
│  └─ check_data.ipynb           ← scripts for testing operations
├─ utils/                        ← utility functions
├─ README.md
└─ requirements.txt
```

## 📥 Installation
- Create and activate a virtual environment (optional but recommended).
- Install dependencies from requirements.txt:
```css
pip install -r requirements.txt
```
DuckDB is used in-process; PySpark will be required once the Spark engine is fully implemented.

## 🚀 Usage
**1. Run data checks with DuckDB**
```python
import pandas as pd
from bigdata_cleaning.core import check_data
from utils.show_struct import show_struct

# Example: load some data into a pandas DataFrame
df = pd.read_csv("your_data.csv")

# Run column-wise checks using DuckDB (default engine)
report = check_data(df, engine="duckdb")

# Visualise the JSON-like report in a notebook
show_struct(report, kind="yaml")
```
- The report contains, for each column:
  - detected data type 
  - missing value counts / percentages 
  - basic numeric overview (non-finite values, negatives, outliers based on IQR or custom ranges)
  - optional uniqueness information (e.g. for string / ID columns) 
- You can use this information to decide which columns should be cleaned and how.

## 🔧 Roadmap / TODO
- Implement full Spark versions of check_data and fix_data.
- Add concrete cleaning rules to fix_data (per-column configuration, e.g. via YAML).
- Extend numeric checks (e.g. domain checks, more advanced outlier handling).
- Add command-line / script entry points to run checks and fixes from the shell.
- Improve documentation and example notebooks.
