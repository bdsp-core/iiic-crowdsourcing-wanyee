"""Supplemental S2: scatter of per-user accuracy vs number of questions answered."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np

from src.data_loading import load_test_df4
from src.plotting import set_default_style, save_figure


def main():
    set_default_style()
    df = load_test_df4()

    per_user = df.groupby("user_id").agg(
        accuracy=("correct", "mean"),
        n_questions=("problem_id", "nunique"),
    ).reset_index()
    per_user.to_csv(ROOT / "figures" / "supp_s2_per_user.csv", index=False)

    # Focus on 1..1000 questions per the paper.
    plot_df = per_user[(per_user["n_questions"] >= 1) & (per_user["n_questions"] <= 1000)]
    corr = float(np.corrcoef(plot_df["n_questions"], plot_df["accuracy"])[0, 1])

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(plot_df["n_questions"], plot_df["accuracy"], s=8, alpha=0.5,
               color="#3a6c89", edgecolor="none")
    ax.set_xlabel("Number of questions answered")
    ax.set_ylabel("Per-user accuracy")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1.05)
    ax.text(0.98, 0.02, f"Pearson r = {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="0.6"))
    fig.suptitle("Accuracy vs number of questions answered (per participant)")

    save_figure(fig, "supp_s2_scatter", ROOT / "figures")
    print(f"Wrote figures/supp_s2_scatter.{{png,pdf}}  (Pearson r={corr:.3f})")


if __name__ == "__main__":
    main()
