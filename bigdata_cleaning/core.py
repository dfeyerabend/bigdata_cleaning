import pandas as pd

# Root function
def check_data(df, engine="duckdb"):
    if engine == "duckdb":
        return check_duckdb(df)
    elif engine == "spark":
        return check_spark(df)
    else:
        raise ValueError("Unknown engine")

# Run data check with DuckDB
def check_duckdb(df):
    raise NotImplementedError("DuckDB engine not implemented yet")

# Run data check with Pyspark
def check_spark(df):
    raise NotImplementedError("Spark engine not implemented yet")