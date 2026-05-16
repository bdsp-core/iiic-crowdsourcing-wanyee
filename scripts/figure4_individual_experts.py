"""Figure 4: Performance of each individual expert versus the crowd as a group.

For each of the 8 experts E_i:
  * expert accuracy = mean of (title == goldstandardnew) on E_i's test rows
  * 95% CI from normal approximation
  * crowd weighted-majority accuracy is the per-problem WM correctness averaged
    over all problems the crowd answered
  * a two-sample z-test compares each expert vs the crowd, with significance
    threshold p < 0.05 (Section 2.9).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

from src.data_loading import load_test_df4
from src.scoring import weighted_majority_correct
from src.plotting import set_default_style, save_figure


def expert_accuracy(df_expert_one: pd.DataFrame) -> tuple[float, float]:
    """Return (mean accuracy, 95% CI half-width) for one expert."""
    correct = df_expert_one["correct"].astype(int).values
    n = len(correct)
    if n == 0:
        return float("nan"), 0.0
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / n)
    return float(p), float(1.96 * se)


def crowd_weighted_majority(df_crowd: pd.DataFrame) -> tuple[float, float]:
    per_problem = df_crowd.groupby("problem_id").apply(weighted_majority_correct)
    n = len(per_problem)
    p = per_problem.mean()
    se = per_problem.std() / np.sqrt(n)
    return float(p), float(1.96 * se)


def main():
    set_default_style()
    df = load_test_df4()

    df_expert = df[df["group"] == "Expert"]
    df_crowd  = df[df["group"] == "Crowd"]

    crowd_acc, crowd_ci = crowd_weighted_majority(df_crowd)

    rows = []
    for i, (uid, sub) in enumerate(df_expert.groupby("user_id"), start=1):
        # Skip the expert if they answered <5 questions for any SRPP (per
        # paper Section 2.9: "any expert who responded to fewer than five
        # questions for any given SRPP was excluded").
        if sub.groupby("goldstandardnew").size().min() < 5:
            continue
        acc, ci = expert_accuracy(sub)
        # Two-sample z-test vs the crowd's mean correctness.
        n_e = len(sub)
        p_e = acc
        se_e = np.sqrt(p_e * (1 - p_e) / n_e)
        z = (p_e - crowd_acc) / np.sqrt(se_e**2 + (crowd_ci / 1.96)**2)
        pval = 2 * (1 - norm.cdf(abs(z)))
        rows.append({"label": f"Expert {i}", "user_id": uid,
                     "accuracy": acc, "ci_half": ci, "n": n_e,
                     "p_vs_crowd": pval, "z_vs_crowd": z})

    rows.append({"label": "Crowd", "user_id": None,
                 "accuracy": crowd_acc, "ci_half": crowd_ci,
                 "n": df_crowd["problem_id"].nunique(),
                 "p_vs_crowd": float("nan"), "z_vs_crowd": float("nan")})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "figures" / "figure4_individual_experts.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    xs = np.arange(len(out))
    colors = []
    for r in out.itertuples():
        if r.label == "Crowd":
            colors.append("#7ab1c4")  # teal
        elif np.isnan(r.p_vs_crowd):
            colors.append("#d8b35a")
        elif r.p_vs_crowd < 0.05 and r.accuracy > crowd_acc:
            colors.append("#9bc792")  # green: expert better
        elif r.p_vs_crowd < 0.05 and r.accuracy < crowd_acc:
            colors.append("#d27d8a")  # red: expert worse
        else:
            colors.append("#e8d486")  # yellow: no diff

    ax.bar(xs, out["accuracy"].values, yerr=out["ci_half"].values,
           color=colors, capsize=4, edgecolor="0.3")
    ax.axhline(crowd_acc, ls="--", color="#84212c", lw=0.8,
               label="Crowd weighted-majority accuracy")
    for x, r in zip(xs, out.itertuples()):
        ax.text(x, r.accuracy + 0.02,
                f"{r.accuracy:.2f}\n[{r.accuracy - r.ci_half:.2f},{r.accuracy + r.ci_half:.2f}]",
                ha="center", fontsize=8)
    ax.set_xticks(xs)
    ax.set_xticklabels(out["label"], rotation=30, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower left")
    fig.suptitle("Individual expert vs crowd (weighted majority)")

    save_figure(fig, "figure4", ROOT / "figures")
    print(f"Wrote figures/figure4.{{png,pdf}}")


if __name__ == "__main__":
    main()
