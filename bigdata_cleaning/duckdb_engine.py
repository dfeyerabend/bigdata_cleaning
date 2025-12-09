import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
    is_datetime64_any_dtype,
)


# -------------------
# Helper Functions
# -------------------

def build_missing_condition(col: str, dtype) -> str:
    """
    Return a DuckDB boolean expression that is TRUE when the value is considered "missing".
    """
    if is_bool_dtype(dtype):
        # booleans: only NULL is missing
        return f"{col} IS NULL"

    elif is_float_dtype(dtype):
        # floats: NULL or NaN
        return f"{col} IS NULL OR isnan({col})"

    elif is_integer_dtype(dtype):
        # ints: only NULL (no NaN)
        return f"{col} IS NULL"

    elif is_string_dtype(dtype):
        # strings: NULL, empty, or typical "null-like" markers
        return (
            f"{col} IS NULL "
            f"OR trim({col}) = '' "
            f"OR lower(trim({col})) IN ('nan', 'none', 'null')"
        )

    elif is_datetime64_any_dtype(dtype):
        # datetimes: only NULL
        return f"{col} IS NULL"

    # fallback for unknown types
    return f"{col} IS NULL"


def compute_numeric_overview(
    con,
    col: str,
    dtype,
    custom_range: tuple[float, float] | None = None,
) -> dict | None:
    """
    Compute neutral statistics for numeric columns:
    - count non-finite values (NaN, ±inf)
    - count negative values
    - IQR-based or custom-range outlier counts
    """
    # only for numeric columns
    if not (is_integer_dtype(dtype) or is_float_dtype(dtype)):
        return None

    # 1) basic counts: non-finite + negatives
    query_counts = f"""
        SELECT
            COUNT(*) AS total_rows,
            SUM(
                CASE
                    WHEN {col} IS NOT NULL AND NOT isfinite({col}) THEN 1
                    ELSE 0
                END
            ) AS n_non_finite,
            SUM(
                CASE
                    WHEN {col} < 0 THEN 1
                    ELSE 0
                END
            ) AS n_negative
        FROM data_table;
    """
    total_rows, n_non_finite, n_negative = con.execute(query_counts).fetchone()

    # 2) decide thresholds (IQR by default, custom if provided)
    if custom_range is not None:
        lower_thresh, upper_thresh = custom_range
        method = "custom_range"
    else:
        # quartiles on finite, non-null values only
        query_quantiles = f"""
            SELECT
                quantile({col}, 0.25) AS q1,
                quantile({col}, 0.75) AS q3
            FROM data_table
            WHERE {col} IS NOT NULL AND isfinite({col});
        """
        q1, q3 = con.execute(query_quantiles).fetchone()

        if q1 is None or q3 is None:
            # column is all NULL / non-finite – nothing to do
            return {
                "total_rows": int(total_rows),
                "N_non_finite": int(n_non_finite),
                "N_negative": int(n_negative),
                "outliers": None,
            }

        iqr = float(q3 - q1)
        lower_thresh = float(q1 - 1.5 * iqr)
        upper_thresh = float(q3 + 1.5 * iqr)
        method = "IQR_1.5"

    # 3) outlier counts (finite, non-null only)
    query_outliers = f"""
        SELECT
            COUNT(*) AS n_finite,
            SUM(CASE WHEN {col} < {lower_thresh} THEN 1 ELSE 0 END) AS n_below_lower,
            SUM(CASE WHEN {col} > {upper_thresh} THEN 1 ELSE 0 END) AS n_above_upper
        FROM data_table
        WHERE {col} IS NOT NULL AND isfinite({col});
    """
    n_finite, n_below_lower, n_above_upper = con.execute(query_outliers).fetchone()

    return {
        "total_rows": int(total_rows),
        "N_non_finite": int(n_non_finite),
        "N_negative": int(n_negative),
        "outliers": {
            "method": method,
            "lower_threshold": float(lower_thresh),
            "upper_threshold": float(upper_thresh),
            "N_finite_used": int(n_finite),
            "N_below_lower": int(n_below_lower),
            "N_above_upper": int(n_above_upper),
        },
    }


def needs_uniqueness_check(col: str, dtype) -> bool:
    """
    Decide whether this column should get a uniqueness check.
    - all string-like columns
    - any column whose name contains 'id' (case-insensitive)
    """
    name = col.lower()
    if "id" in name:
        return True
    if is_string_dtype(dtype):
        return True
    return False


# -----------------------
# Main engine functions
# -----------------------

def check_duckdb(df: pd.DataFrame, custom_numeric_ranges: dict[str, tuple] | None = None) -> dict:
    import duckdb

    report: dict = {}

    con = duckdb.connect()
    try:
        # make the DataFrame available as "data_table" inside DuckDB
        con.register("data_table", df)

        for col, dtype in df.dtypes.items():
            col_report = {
                "dtype": str(dtype),
                "issues": {
                    "missing_values": {},
                    "numeric_overview": {},
                    "uniqueness": {},
                },
            }

            # --- 1) Missing data ---
            missing_cond = build_missing_condition(col, dtype)
            query_missing = f"""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN {missing_cond} THEN 1 ELSE 0 END) AS missing
                FROM data_table
            """
            total, missing = con.execute(query_missing).fetchone()
            pct_missing = round((missing / total) * 100, 2) if total else 0.0

            col_report["issues"]["missing_values"] = {
                "N_missing": int(missing),
                "pct_missing": pct_missing,
            }

            # --- numeric overview (only for numeric columns) ---
            custom_range = None
            if custom_numeric_ranges and col in custom_numeric_ranges:
                custom_range = custom_numeric_ranges[col]

            numeric_info = compute_numeric_overview(con, col, dtype, custom_range)
            col_report["issues"]["numeric_overview"] = numeric_info

            # --- 3) Uniqueness (selected columns only) ---
            if needs_uniqueness_check(col, dtype):
                query_unique = f"""
                    SELECT
                        COUNT(*) AS total,
                        COUNT(DISTINCT {col}) AS n_unique
                    FROM data_table
                """
                total_u, n_unique = con.execute(query_unique).fetchone()
                pct_unique = (
                    round((n_unique / total_u) * 100, 2) if total_u else 0.0
                )

                col_report["issues"]["uniqueness"] = {
                    "N_unique": int(n_unique),
                    "pct_unique": pct_unique,
                }
            else:
                col_report["issues"]["uniqueness"] = None

            report[col] = col_report

    finally:
        con.close()

    return report


def fix_duckdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Placeholder for future cleaning logic.
    For now it just returns the original DataFrame unchanged.
    """
    return df