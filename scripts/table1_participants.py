"""Table 1: number of questions answered and users per group.

Reproduces both blocks of the paper's Table 1: calibration dataset (top
block in the published table) and test dataset (bottom block). Counts come
from the per-user eligibility filter described in Section 2.3.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data_loading import load_test_df4


GROUP_MAP = {
    "Expert":                    ("Expert", "Expert"),
    "MD":                        ("MD", "MD (all)"),
    "DO":                        ("MD", "DO"),
    "Medical Student":           ("Medical student", "Medical student (all)"),
    "NP":                        ("NP/PA/pharmacist", "NP (all)"),
    "PA":                        ("NP/PA/pharmacist", "PA"),
    "Pharmacist":                ("NP/PA/pharmacist", "Pharmacist"),
    "NP Student":                ("Other students", "NP student"),
    "PA Student":                ("Other students", "PA student"),
    "Pharmacy Student":          ("Other students", "Pharmacy student (all)"),
    "Other Healthcare Student":  ("Other students", "Other healthcare student (all)"),
    "Other":                     ("Others", "Others (all)"),
}


def _summary(sub: pd.DataFrame) -> pd.DataFrame:
    sub = sub.copy()
    sub["Group"] = sub["experience_level"].map(lambda x: GROUP_MAP.get(x, ("Unknown", x))[0])
    sub["Experience level"] = sub["experience_level"].map(
        lambda x: GROUP_MAP.get(x, ("Unknown", x))[1]
    )
    out = (sub.groupby(["Group", "Experience level"])
              .agg(n_questions=("problem_id", "count"),
                   n_users=("user_id", "nunique"))
              .reset_index())
    out["questions/users"] = out["n_questions"].astype(str) + "/" + out["n_users"].astype(str)
    return out


def main():
    df = load_test_df4()

    print("=" * 70)
    print("CALIBRATION DATASET")
    print("=" * 70)
    calib = _summary(df[df["in_calibration"]])
    print(calib.to_string(index=False))
    print(f"\nCalibration totals: {calib['n_questions'].sum():,} questions, "
          f"{df.loc[df['in_calibration'], 'user_id'].nunique():,} users")

    print("\n" + "=" * 70)
    print("TEST DATASET")
    print("=" * 70)
    test = _summary(df[~df["in_calibration"]])
    print(test.to_string(index=False))
    print(f"\nTest totals: {test['n_questions'].sum():,} questions, "
          f"{df.loc[~df['in_calibration'], 'user_id'].nunique():,} users")

    out_dir = ROOT / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    calib.to_csv(out_dir / "table1_calibration.csv", index=False)
    test.to_csv(out_dir / "table1_test.csv", index=False)
    print(f"\nWrote {out_dir / 'table1_{calibration,test}.csv'}")


if __name__ == "__main__":
    main()
