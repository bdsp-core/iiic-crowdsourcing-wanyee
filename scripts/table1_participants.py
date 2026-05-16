"""Table 1: number of questions answered and users per group (calibration + test).

The original notebook (csvforeachexpertlevel...ipynb) computes this from
test_df4.csv after applying the calibration/test split. Calibration counts
come from a separate ``calibration_df`` not present in the shared data; this
script reproduces the part of Table 1 we can build from test_df4 alone, which
is the **test-set row counts** (the larger block of Table 1).

If you have the calibration dataframe, set CALIB_PATH below.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data_loading import load_test_df4


# Map raw Centaur Labs experience_level values to the paper's groupings.
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


def main():
    df = load_test_df4()

    df["Group"] = df["experience_level"].map(lambda x: GROUP_MAP.get(x, ("Unknown", x))[0])
    df["Experience level"] = df["experience_level"].map(
        lambda x: GROUP_MAP.get(x, ("Unknown", x))[1]
    )

    tbl = (df.groupby(["Group", "Experience level"])
             .agg(n_questions=("problem_id", "count"),
                  n_users=("user_id", "nunique"))
             .reset_index())
    tbl["questions/users"] = tbl["n_questions"].astype(str) + "/" + tbl["n_users"].astype(str)
    print(tbl.to_string(index=False))

    out = ROOT / "figures" / "table1_test_dataset.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    tbl.to_csv(out, index=False)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
