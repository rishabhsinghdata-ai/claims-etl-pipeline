"""Claims ETL pipeline."""
import pandas as pd


def extract(path: str) -> pd.DataFrame:
    """Read raw claims data from a CSV file."""
    return pd.read_csv(path)
