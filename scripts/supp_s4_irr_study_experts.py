"""Supplemental S4: inter-rater agreement metrics for the 8 Experts in Study.

For each EEG-pattern subgroup (and Overall): the number of segments, the
mean pairwise agreement, Fleiss' kappa with its expected-agreement Pe(F),
and Gwet's AC1 with its expected-agreement Pe(G).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import SRPPS
from src.data_loading import load_test_df4
from src.irr import irr_metrics_by_pattern, long_to_wide


def main():
    df = load_test_df4()
    df_e = df[df["group"] == "Expert"].copy()

    wide = long_to_wide(df_e)              # items x experts
    # Attach gold standard for the by-pattern slicing.
    gold = (df_e.drop_duplicates("problem_id")
                .set_index("problem_id")["goldstandardnew"])
    wide["goldstandardnew"] = gold

    tbl = irr_metrics_by_pattern(wide, categories=SRPPS)
    print(tbl.to_string(index=False))

    out = ROOT / "figures" / "supp_s4_irr_study_experts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    tbl.to_csv(out, index=False)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
