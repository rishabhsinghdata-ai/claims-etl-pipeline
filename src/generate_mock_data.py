"""Generate a messy mock insurance claims dataset for the ETL pipeline."""
import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

DIAGNOSIS_CODES = ["J06.9", "I10", "E11.9", "M54.5", "K21.9", "F41.9", "Z00.00"]
STATUSES = ["approved", "rejected", "APPROVED", "Rejected", None]


def generate(n_rows: int = 200) -> pd.DataFrame:
    start = date(2025, 1, 1)
    rows = []
    for i in range(n_rows):
        rows.append(
            {
                "Policy ID": f"POL{random.randint(1000, 1060)}",
                "Claim Date": (start + timedelta(days=random.randint(0, 600))).isoformat(),
                "Claim Amount": round(random.uniform(50, 12000), 2) if random.random() > 0.05 else None,
                "Diagnosis Code": random.choice(DIAGNOSIS_CODES) if random.random() > 0.04 else None,
                "Status": random.choice(STATUSES),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate()
    df.to_csv("data/claims_raw.csv", index=False)
    print(f"Wrote {len(df)} rows to data/claims_raw.csv")
