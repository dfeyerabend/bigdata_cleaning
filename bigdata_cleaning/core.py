
# Logic for loading check data functions from engines
def check_data(df, engine="duckdb", custom_numeric_ranges=None):
    if engine == "duckdb":
        from .duckdb_engine import check_duckdb
        return check_duckdb(df, custom_numeric_ranges)
    elif engine == "spark":
        from .spark_engine import check_spark
        return check_spark(df, custom_numeric_ranges)
    else:
        raise ValueError("Unknown engine")

# Logic for loading fix data functions from engines
def fix_data(df, engine="duckdb"):
    if engine == "duckdb":
        from .duckdb_engine import fix_duckdb
        return fix_duckdb(df)
    elif engine == "spark":
        from .spark_engine import fix_spark
        return fix_spark(df)
    else:
        raise ValueError(f"Unknown engine: {engine}")