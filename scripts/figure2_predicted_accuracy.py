"""Figure 2: Predicted accuracy (NW + WM) for Expert vs Crowd, overall and per SRPP.

Fits the four mixed-effects models from Section 2.4-2.5, extracts the adjusted
predicted accuracy per (pattern, scoring, group), and renders the horizontal
grouped bar chart shown as Figure 2 in the paper.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loading import load_test_df4
from src.mixed_models import fit_all_models
from src.plotting import COLORS, LABEL_PRETTY, set_default_style, save_figure


def predicted_summary(agg: pd.DataFrame, scoring: str,
                      pattern_col: str | None = None) -> pd.DataFrame:
    """Mean +/- 1.96*SE of the model's adjusted predicted accuracy."""
    keys = ["group"] + ([pattern_col] if pattern_col else [])
    s = (agg.groupby(keys)["predicted_accuracy"]
            .agg(["mean", "std", "count"])
            .reset_index())
    s["se"] = s["std"] / np.sqrt(s["count"])
    s["ci"] = 1.96 * s["se"]
    s["scoring"] = scoring
    if not pattern_col:
        s["pattern"] = "Overall"
    else:
        s = s.rename(columns={pattern_col: "pattern"})
    return s[["pattern", "group", "scoring", "mean", "se", "ci"]]


def main():
    set_default_style()
    df = load_test_df4()
    models = fit_all_models(df)

    summary = pd.concat([
        predicted_summary(models["agg_overall_NW"], "NW"),
        predicted_summary(models["agg_pattern_NW"], "NW", "pattern"),
        predicted_summary(models["agg_overall_WM"], "WM"),
        predicted_summary(models["agg_pattern_WM"], "WM", "pattern"),
    ], ignore_index=True)
    summary.to_csv(ROOT / "figures" / "figure2_predicted_accuracy.csv", index=False)

    # Ordering: Overall on top, then SRPPs alphabetically.
    patterns_order = ["Overall"] + sorted(
        [p for p in summary["pattern"].unique() if p != "Overall"]
    )
    fig, ax = plt.subplots(figsize=(8, 7))

    y = np.arange(len(patterns_order))
    offsets = {("NW", "Expert"): -0.27, ("NW", "Crowd"): -0.09,
               ("WM", "Expert"):  0.09, ("WM", "Crowd"):  0.27}
    colors = {("NW", "Expert"): COLORS["Expert_NW"],
              ("NW", "Crowd"):  COLORS["Crowd_NW"],
              ("WM", "Expert"): COLORS["Expert_WM"],
              ("WM", "Crowd"):  COLORS["Crowd_WM"]}

    for (scoring, group), off in offsets.items():
        d = summary[(summary["scoring"] == scoring) & (summary["group"] == group)]
        d = d.set_index("pattern").reindex(patterns_order)
        ax.barh(y + off, d["mean"].values, height=0.16,
                xerr=d["ci"].values, color=colors[(scoring, group)],
                error_kw={"capsize": 2, "lw": 0.8, "ecolor": "0.3"},
                label=f"{group} ({scoring})")
        # Numeric label.
        for yi, v in zip(y + off, d["mean"].values):
            if not np.isnan(v):
                ax.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=8)

    ax.set_yticks(y)
    ax.set_yticklabels([LABEL_PRETTY.get(p.lower(), p) for p in patterns_order])
    ax.invert_yaxis()
    ax.set_xlabel("Predicted Accuracy")
    ax.set_xlim(0, 1.0)
    ax.legend(loc="lower right", title="Group (Scoring)")
    fig.suptitle("Performance of Crowd vs Experts: non-weighted (NW) and weighted majority (WM)")

    save_figure(fig, "figure2", ROOT / "figures")
    print(f"Wrote figures/figure2.{{png,pdf}}")


if __name__ == "__main__":
    main()
