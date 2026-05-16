"""Figure 5: Crowd performance vs sample size (5..50 raters, 1000 bootstraps).

This is the slow step in the reproduction. Override --n-bootstrap (default
1000) at the command line to trade speed for precision.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

from src.data_loading import load_test_df4
from src.bootstrap import sample_size_curve
from src.plotting import set_default_style, save_figure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    set_default_style()
    df = load_test_df4()

    curve = sample_size_curve(df, sizes=range(5, 55, 5),
                              n_bootstrap=args.n_bootstrap, seed=args.seed)
    curve.to_csv(ROOT / "figures" / "figure5_bootstrap.csv", index=False)
    expert_acc = curve.attrs["expert_acc"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(curve["sample_size"], curve["mean_acc"],
                yerr=[curve["mean_acc"] - curve["ci_lower"],
                      curve["ci_upper"] - curve["mean_acc"]],
                fmt="o-", color="#3a6c89", capsize=3,
                label="Crowd (bootstrap)")
    ax.axhline(expert_acc, ls="-", color="#84212c", lw=1.0,
               label=f"Expert WM accuracy ({expert_acc:.2f})")
    for _, r in curve.iterrows():
        ax.text(r["sample_size"], r["mean_acc"] + 0.015,
                f"{r['mean_acc']:.2f}", ha="center", fontsize=8)

    ax.set_xlabel("Sample size (number of crowd users)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.0)
    ax.legend(loc="lower right")
    fig.suptitle("Crowd weighted-majority accuracy vs number of raters")

    save_figure(fig, "figure5", ROOT / "figures")
    print(f"Wrote figures/figure5.{{png,pdf}}")


if __name__ == "__main__":
    main()
