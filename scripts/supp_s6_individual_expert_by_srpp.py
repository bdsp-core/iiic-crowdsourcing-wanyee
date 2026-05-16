"""Supplemental S6: per-SRPP, each individual expert vs the crowd's WM accuracy.

Six panels (one per SRPP), each showing 8 expert bars + one crowd bar with
95% CIs. Each panel uses only the rows whose ``goldstandardnew`` equals that
SRPP.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.config import SRPPS
from src.data_loading import load_test_df4
from src.scoring import weighted_majority_correct
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def main():
    set_default_style()
    df = load_test_df4()

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
    rows = []
    for ax, pat in zip(axes.flat, SRPPS):
        sub = df[df["goldstandardnew"] == pat]
        if sub.empty:
            ax.set_visible(False)
            continue
        # Expert bars.
        exp = sub[sub["group"] == "Expert"]
        crowd = sub[sub["group"] == "Crowd"]

        bars = []
        for i, (uid, eg) in enumerate(exp.groupby("user_id"), start=1):
            if len(eg) < 5:
                continue
            p = eg["correct"].mean()
            se = np.sqrt(p * (1 - p) / len(eg))
            bars.append((f"E{i}", p, 1.96 * se))
            rows.append({"pattern": pat, "label": f"E{i}", "accuracy": p,
                         "ci_half": 1.96 * se, "user_id": uid})

        # Crowd WM accuracy on this SRPP.
        per_q = crowd.groupby("problem_id").apply(weighted_majority_correct)
        crowd_p = per_q.mean()
        crowd_se = per_q.std() / np.sqrt(len(per_q))
        bars.append(("Crowd", crowd_p, 1.96 * crowd_se))
        rows.append({"pattern": pat, "label": "Crowd",
                     "accuracy": crowd_p, "ci_half": 1.96 * crowd_se, "user_id": None})

        labels = [b[0] for b in bars]
        vals = [b[1] for b in bars]
        cis = [b[2] for b in bars]
        colors = ["#e8d486"] * (len(bars) - 1) + ["#7aa9d4"]
        xs = np.arange(len(bars))
        ax.bar(xs, vals, yerr=cis, color=colors, capsize=3, edgecolor="0.3")
        ax.axhline(crowd_p, ls="--", color="#7aa9d4", lw=0.8)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, rotation=45, fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_title(LABEL_PRETTY.get(pat, pat))

    for ax in axes[:, 0]:
        ax.set_ylabel("Accuracy")

    fig.suptitle("Individual experts vs crowd weighted majority, by SRPP")
    fig.tight_layout()

    out = ROOT / "figures" / "supp_s6_per_srpp.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    save_figure(fig, "supp_s6_individual_expert_by_srpp", ROOT / "figures")
    print(f"Wrote figures/supp_s6_individual_expert_by_srpp.{{png,pdf}}")


if __name__ == "__main__":
    main()
