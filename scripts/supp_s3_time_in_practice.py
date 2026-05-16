"""Supplemental S3: time in practice for the 8 study experts and 30 gold-standard experts.

This table is not generated from data; the values are taken from the paper.
Provided here for reproducibility / cross-check.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd


STUDY_EXPERTS = [
    ("E1", 1), ("E2", 2.5), ("E3", 15), ("E4", 5),
    ("E5", 10), ("E6", 2), ("E7", 10), ("E8", 5),
]

GOLD_STANDARD_EXPERTS = [
    ("E1", 7),  ("E2", 4),  ("E3", 7),  ("E4", 4),  ("E5", 9),  ("E6", 8),
    ("E7", 5),  ("E8", 9),  ("E9", 5),  ("E10", 6), ("E11", 10),("E12", 10),
    ("E13", 8), ("E14", 18),("E15", 15),("E16", 2), ("E17", 9), ("E18", 11),
    ("E19", 5), ("E20", 7), ("E21", 4), ("E22", 4), ("E23", 9), ("E24", 6),
    ("E25", 35),("E26", 8), ("E27", 5), ("E28", 13),("E29", 22),("E30", 3),
]


def main():
    study = pd.DataFrame(STUDY_EXPERTS, columns=["Expert", "Years in practice"])
    gold  = pd.DataFrame(GOLD_STANDARD_EXPERTS, columns=["Expert", "Years in practice"])

    out_dir = ROOT / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    study.to_csv(out_dir / "supp_s3_study_experts.csv", index=False)
    gold.to_csv(out_dir / "supp_s3_goldstandard_experts.csv", index=False)
    print(f"Study experts (n={len(study)}):  mean = {study['Years in practice'].mean():.1f}")
    print(f"Gold std experts (n={len(gold)}): mean = {gold['Years in practice'].mean():.1f}")
    print(f"Wrote {out_dir / 'supp_s3_*.csv'}")


if __name__ == "__main__":
    main()
