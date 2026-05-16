"""Supplemental S11: per-SRPP histograms of crowd accuracy.

Each user has one per-SRPP accuracy column in test_df4:
  ``GPDaccuracy``, ``LPDaccuracy``, ``grdaaccuracy``, ``lrdaaccuracy``,
  ``otheraccuracy``, ``seizureaccuracy``.

We pull these from test_df4 (one row per user-question, with the user's
overall accuracy duplicated across rows -- so we first drop duplicates by
user_id) and plot 6 histograms with a vertical line at the overall mean
across all SRPPs.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from src.config import SRPPS
from src.data_loading import load_test_df4
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


COL_MAP = {
    "gpd":     "GPDaccuracy",
    "lpd":     "LPDaccuracy",
    "grda":    "grdaaccuracy",
    "lrda":    "lrdaaccuracy",
    "other":   "otheraccuracy",
    "seizure": "seizureaccuracy",
}


def main():
    set_default_style()
    df = load_test_df4()
    per_user = df.drop_duplicates("user_id").set_index("user_id")

    # The paper's histograms focus on the crowd, not experts.
    per_user = per_user[per_user["experience_level"] != "Expert"]

    bins = np.arange(0, 1.05, 0.05)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    grand_mean = per_user["combined_accuracy"].mean()

    for ax, pat in zip(axes.flat, SRPPS):
        col = COL_MAP[pat]
        if col not in per_user.columns:
            ax.set_visible(False)
            continue
        v = per_user[col].dropna()
        ax.hist(v, bins=bins, color="#3a6c89", edgecolor="white")
        ax.axvline(grand_mean, color="#84212c", ls="--", lw=1,
                   label=f"Overall mean = {grand_mean:.2f}")
        ax.set_title(f"{LABEL_PRETTY[pat]} (mean={v.mean():.2f})")
        ax.set_xlabel("Accuracy"); ax.set_ylabel("Count")
        ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("Supp S11: distribution of per-user crowd accuracy by SRPP")
    fig.tight_layout()
    save_figure(fig, "supp_s11_accuracy_histograms", ROOT / "figures")
    print("Wrote figures/supp_s11_accuracy_histograms.{png,pdf}")


if __name__ == "__main__":
    main()
