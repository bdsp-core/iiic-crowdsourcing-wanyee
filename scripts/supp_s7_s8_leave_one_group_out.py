"""Supplementals S7 & S8: leave-one-group-out sensitivity analyses.

Five crowd subgroups (see src.config.CROWD_SUBGROUPS). For each subgroup g:
   * drop g from the crowd
   * recompute the crowd's weighted-majority accuracy
   * compare against the experts' WM accuracy and the full-crowd WM accuracy
S7: overall (one panel). S8: per SRPP (6 panels).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.config import CROWD_SUBGROUPS, SRPPS
from src.data_loading import load_test_df4
from src.scoring import weighted_majority_correct
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def wm_accuracy(df: pd.DataFrame) -> tuple[float, float]:
    per_q = df.groupby("problem_id").apply(weighted_majority_correct)
    if per_q.empty:
        return float("nan"), 0.0
    m = float(per_q.mean())
    se = float(per_q.std() / np.sqrt(len(per_q)))
    return m, 1.96 * se


def compute_logo(df: pd.DataFrame, pattern: str | None = None) -> pd.DataFrame:
    if pattern:
        df = df[df["goldstandardnew"] == pattern]
    expert = df[df["group"] == "Expert"]
    crowd  = df[df["group"] == "Crowd"]

    rows = []
    e_mean, e_ci = wm_accuracy(expert)
    rows.append({"group": "Expert", "mean": e_mean, "ci_half": e_ci})
    c_mean, c_ci = wm_accuracy(crowd)
    rows.append({"group": "Crowd (all)", "mean": c_mean, "ci_half": c_ci})

    for label, levels in CROWD_SUBGROUPS.items():
        kept = crowd[~crowd["experience_level"].isin(levels)]
        m, ci = wm_accuracy(kept)
        rows.append({"group": f"Crowd \\ {label}", "mean": m, "ci_half": ci})
    return pd.DataFrame(rows)


def _plot(ax, df: pd.DataFrame, title: str):
    xs = np.arange(len(df))
    colors = (["#3a6c89"] +                # Expert
              ["#84212c"] +                # Full crowd
              ["#9bc792"] * (len(df) - 2)) # Subsetted crowd bars
    ax.bar(xs, df["mean"], yerr=df["ci_half"], color=colors,
           capsize=3, edgecolor="0.3")
    for x, v in zip(xs, df["mean"]):
        if not np.isnan(v):
            ax.text(x, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    ax.set_xticks(xs)
    ax.set_xticklabels(df["group"].tolist(), rotation=35, ha="right", fontsize=8)
    ax.set_ylim(0, 1.0)
    ax.set_title(title)


def main():
    set_default_style()
    df = load_test_df4()

    # S7: Overall.
    fig, ax = plt.subplots(figsize=(8, 5))
    overall = compute_logo(df)
    overall.to_csv(ROOT / "figures" / "supp_s7_logo_overall.csv", index=False)
    _plot(ax, overall, "Overall")
    fig.suptitle("Supp S7: Leave-one-group-out (overall WM accuracy)")
    save_figure(fig, "supp_s7_logo_overall", ROOT / "figures")
    plt.close(fig)
    print("Wrote figures/supp_s7_logo_overall.{png,pdf}")

    # S8: per SRPP.
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    per_pattern_rows = []
    for ax, pat in zip(axes.flat, SRPPS):
        d = compute_logo(df, pattern=pat)
        d.insert(0, "pattern", pat)
        per_pattern_rows.append(d)
        _plot(ax, d.drop(columns="pattern"), LABEL_PRETTY[pat])
    fig.suptitle("Supp S8: Leave-one-group-out by SRPP")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    pd.concat(per_pattern_rows, ignore_index=True).to_csv(
        ROOT / "figures" / "supp_s8_logo_per_srpp.csv", index=False
    )
    save_figure(fig, "supp_s8_logo_per_srpp", ROOT / "figures")
    print("Wrote figures/supp_s8_logo_per_srpp.{png,pdf}")


if __name__ == "__main__":
    main()
