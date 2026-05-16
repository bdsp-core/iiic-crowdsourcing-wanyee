"""One-shot reproducer for every figure and table in the paper.

Usage
-----
$ python scripts/reproduce_all.py
$ python scripts/reproduce_all.py --skip figure5  # skip slow bootstrap
$ python scripts/reproduce_all.py --only figure2 figure3
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Module name (relative to scripts/) -> short id we use in --only/--skip.
ALL_TARGETS = {
    "table1":   "scripts.table1_participants",
    "figure2":  "scripts.figure2_predicted_accuracy",
    "figure3":  "scripts.figure3_forest_plot",
    "figure4":  "scripts.figure4_individual_experts",
    "figure5":  "scripts.figure5_bootstrap_samplesize",     # slow (~1000 bootstraps)
    "supp_s1":  "scripts.supp_s1_countries",
    "supp_s2":  "scripts.supp_s2_accuracy_vs_questions",
    "supp_s3":  "scripts.supp_s3_time_in_practice",
    "supp_s4":  "scripts.supp_s4_irr_study_experts",
    "supp_s5":  "scripts.supp_s5_violin_studyvsgold",       # requires labels_experts30.xlsx
    "supp_s6":  "scripts.supp_s6_individual_expert_by_srpp",
    "supp_s78": "scripts.supp_s7_s8_leave_one_group_out",
    "supp_s9":  "scripts.supp_s9_hardfilter",
    "supp_s10": "scripts.supp_s10_subgroup_forest",
    "supp_s11": "scripts.supp_s11_accuracy_histograms",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", nargs="+", choices=ALL_TARGETS.keys(), default=None)
    p.add_argument("--skip", nargs="+", choices=ALL_TARGETS.keys(), default=[])
    args = p.parse_args()

    targets = args.only or list(ALL_TARGETS.keys())
    targets = [t for t in targets if t not in args.skip]

    for t in targets:
        mod_name = ALL_TARGETS[t]
        t0 = time.time()
        print(f"\n==== {t}  ({mod_name})  ====")
        try:
            mod = importlib.import_module(mod_name)
            mod.main()
        except FileNotFoundError as e:
            print(f"  [SKIP] missing input file: {e}")
            continue
        except Exception as e:
            print(f"  [FAIL] {type(e).__name__}: {e}")
            continue
        print(f"  done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
