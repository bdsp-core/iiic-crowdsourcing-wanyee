"""Supplemental S9: hard-filtered crowd (bottom-20% removed) vs unfiltered.

Section 2.10 of the paper: "By applying a hard filter that excludes the
bottom 20% of crowd raters based on calibration set accuracy ... their
average performance on the test dataset (using non-majority weighted
scoring) gained improvement ranging from .02 to .05".

Reproduces this by computing the 20th-percentile threshold on
``combined_accuracy`` (the per-user calibration accuracy) and rerunning the
non-weighted overall + per-pattern means.
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
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def per_group_means(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pat in ["Overall"] + SRPPS:
        sub = df if pat == "Overall" else df[df["goldstandardnew"] == pat]
        for g in ("Expert", "Crowd"):
            sg = sub[sub["group"] == g]
            if sg.empty:
                continue
            p = sg["correct"].mean()
            se = sg["correct"].std() / np.sqrt(len(sg))
            rows.append({"pattern": pat, "group": g, "mean": p,
                         "ci_half": 1.96 * se})
    return pd.DataFrame(rows)


def main():
    set_default_style()
    df = load_test_df4()
    crowd = df[df["group"] == "Crowd"]
    threshold = crowd["combined_accuracy"].quantile(0.2)
    print(f"Bottom-20% combined_accuracy threshold: {threshold:.3f}")

    keep_mask = (df["group"] == "Expert") | (df["combined_accuracy"] >= threshold)
    df_hf = df[keep_mask].copy()

    raw = per_group_means(df).assign(filter="unfiltered")
    hf  = per_group_means(df_hf).assign(filter="hard-filtered")
    out = pd.concat([raw, hf], ignore_index=True)
    out.to_csv(ROOT / "figures" / "supp_s9_hardfilter.csv", index=False)

    order = ["Overall"] + SRPPS
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.18
    x = np.arange(len(order))
    cfg = [("Expert", "unfiltered", -1.5*width, "#3a6c89"),
           ("Crowd",  "unfiltered", -0.5*width, "#84212c"),
           ("Expert", "hard-filtered",  0.5*width, "#7aa9d4"),
           ("Crowd",  "hard-filtered",  1.5*width, "#f0c987")]
    for g, f, off, color in cfg:
        d = out[(out["group"] == g) & (out["filter"] == f)].set_index("pattern").reindex(order)
        ax.bar(x + off, d["mean"], width=width, yerr=d["ci_half"],
               color=color, capsize=2, label=f"{g} ({f})", edgecolor="0.4")
    ax.set_xticks(x)
    ax.set_xticklabels([LABEL_PRETTY.get(p.lower(), p) for p in order], rotation=20)
    ax.set_ylabel("Proportion correct (NW)")
    ax.set_ylim(0, 1.0)
    ax.legend(loc="lower right", ncol=2)
    fig.suptitle("Hard-filtered crowd (bottom 20% removed) vs unfiltered")

    save_figure(fig, "supp_s9_hardfilter", ROOT / "figures")
    print("Wrote figures/supp_s9_hardfilter.{png,pdf}")


if __name__ == "__main__":
    main()
