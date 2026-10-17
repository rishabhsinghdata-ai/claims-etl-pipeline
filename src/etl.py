"""Claims ETL pipeline."""
import pandas as pd


def extract(path: str) -> pd.DataFrame:
    """Read raw claims data from a CSV file."""
    return pd.read_csv(path)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to lowercase snake_case."""
    out = df.copy()
    out.columns = [c.strip().lower().replace(" ", "_") for c in out.columns]
    return out


def clean_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise status to lowercase; fill missing with 'unknown'."""
    out = df.copy()
    out["status"] = out["status"].str.strip().str.lower().fillna("unknown")
    return out


def clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with no claim amount; fill missing diagnosis code."""
    out = df.dropna(subset=["claim_amount"]).copy()
    out["diagnosis_code"] = out["diagnosis_code"].fillna("UNKNOWN")
    return out


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert claim_date from string to datetime."""
    out = df.copy()
    out["claim_date"] = pd.to_datetime(out["claim_date"])
    return out


def filter_decided_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only approved or rejected claims."""
    return df[df["status"].isin(["approved", "rejected"])].copy()


def add_claim_band(df: pd.DataFrame) -> pd.DataFrame:
    """Add a calculated field bucketing claims by size."""
    out = df.copy()
    out["claim_band"] = pd.cut(
        out["claim_amount"],
        bins=[0, 500, 2000, 5000, float("inf")],
        labels=["small", "medium", "large", "very_large"],
    )
    return out


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Run all transformations in the required order."""
    out = rename_columns(df)
    out = clean_status(out)
    out = clean_nulls(out)
    out = parse_dates(out)
    out = filter_decided_claims(out)
    out = add_claim_band(out)
    return out.reset_index(drop=True)


def load(df: pd.DataFrame, path: str) -> None:
    """Write the transformed data to a CSV file."""
    df.to_csv(path, index=False)


def main(
    input_path: str = "data/claims_raw.csv",
    output_path: str = "data/claims_clean.csv",
) -> None:
    raw = extract(input_path)
    clean = transform(raw)
    load(clean, output_path)
    print(f"Read {len(raw)} rows, wrote {len(clean)} rows to {output_path}")


if __name__ == "__main__":
    main()
