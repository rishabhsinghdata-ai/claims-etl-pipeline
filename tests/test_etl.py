import pandas as pd
import pytest

from src.etl import (
    add_claim_band,
    clean_nulls,
    clean_status,
    filter_decided_claims,
    parse_dates,
    rename_columns,
    transform,
)


def test_rename_columns_makes_snake_case():
    df = pd.DataFrame(columns=["Policy ID", "Claim Date", " Claim Amount "])
    result = rename_columns(df)
    assert list(result.columns) == ["policy_id", "claim_date", "claim_amount"]


def test_clean_status_normalises_case_and_fills_nulls():
    df = pd.DataFrame({"status": ["APPROVED", "Rejected", None, " approved "]})
    result = clean_status(df)
    assert list(result["status"]) == ["approved", "rejected", "unknown", "approved"]


def test_clean_nulls_drops_missing_amounts():
    df = pd.DataFrame(
        {"claim_amount": [100.0, None, 300.0], "diagnosis_code": ["I10", "I10", None]}
    )
    result = clean_nulls(df)
    assert len(result) == 2
    assert result["claim_amount"].notna().all()


def test_clean_nulls_fills_missing_diagnosis():
    df = pd.DataFrame({"claim_amount": [100.0], "diagnosis_code": [None]})
    result = clean_nulls(df)
    assert result["diagnosis_code"].iloc[0] == "UNKNOWN"


def test_parse_dates_returns_datetime_type():
    df = pd.DataFrame({"claim_date": ["2025-04-15", "2025-06-13"]})
    result = parse_dates(df)
    assert pd.api.types.is_datetime64_any_dtype(result["claim_date"])


def test_filter_decided_claims_removes_unknown():
    df = pd.DataFrame({"status": ["approved", "rejected", "unknown", "approved"]})
    result = filter_decided_claims(df)
    assert len(result) == 3
    assert "unknown" not in set(result["status"])


@pytest.mark.parametrize(
    "amount, expected",
    [(100, "small"), (1000, "medium"), (3000, "large"), (9000, "very_large")],
)
def test_add_claim_band_buckets_correctly(amount, expected):
    df = pd.DataFrame({"claim_amount": [float(amount)]})
    result = add_claim_band(df)
    assert result["claim_band"].iloc[0] == expected


def test_transformations_do_not_mutate_input():
    df = pd.DataFrame({"status": ["APPROVED"]})
    clean_status(df)
    assert df["status"].iloc[0] == "APPROVED"


def test_transform_end_to_end_row_count_and_columns():
    raw = pd.DataFrame(
        {
            "Policy ID": ["POL1", "POL2", "POL3", "POL4"],
            "Claim Date": ["2025-01-01"] * 4,
            "Claim Amount": [100.0, None, 2500.0, 800.0],
            "Diagnosis Code": ["I10", "I10", None, "E11.9"],
            "Status": ["APPROVED", "rejected", "Rejected", None],
        }
    )
    result = transform(raw)
    # POL2 dropped (null amount), POL4 dropped (unknown status)
    assert len(result) == 2
    assert list(result["policy_id"]) == ["POL1", "POL3"]
    assert "claim_band" in result.columns
    assert list(result.index) == [0, 1]