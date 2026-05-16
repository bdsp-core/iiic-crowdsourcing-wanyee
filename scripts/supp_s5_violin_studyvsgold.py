"""Supplemental S5: split-violin of pairwise agreement (study experts vs 30 gold-std experts).

Builds two long-format pairwise-agreement frames -- one for the 8 study experts
(from test_df4) and one for the 30 gold-standard experts (from
labels_experts30.xlsx) -- and plots a split violin per SRPP + Overall.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loading import load_test_df4, load_experts30
from src.irr import pairwise_overall, pairwise_by_pattern
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def study_expert_pairs(df) -> pd.DataFrame:
    df_e = df[df["group"] == "Expert"].copy()
    overall = pairwise_overall(df_e).assign(pattern="Overall")
    per_p = pairwise_by_pattern(df_e)
    return pd.concat([overall, per_p], ignore_index=True).assign(source="Study Experts")


def gold_expert_pairs(dfg) -> pd.DataFrame:
    """Compute pairwise agreement for the 30 gold-standard experts."""
    from itertools import combinations
    exclude = {"file_name", "goldstandardnew", "found_labels"}
    expert_cols = [c for c in dfg.columns if c not in exclude]

    rows_overall, rows_pattern = [], []
    # Overall.
    for a, b in combinations(expert_cols, 2):
        v = dfg[a].notnull() & dfg[b].notnull()
        n = int(v.sum())
        if n <= 5:
            continue
        agree = int((dfg.loc[v, a] == dfg.loc[v, b]).sum())
        rows_overall.append({"rater_a": a, "rater_b": b,
                             "n_overlap": n, "agreement": agree / n,
                             "pattern": "Overall"})
    # By pattern.
    for p in dfg["goldstandardnew"].dropna().unique():
        sub = dfg[dfg["goldstandardnew"] == p]
        for a, b in combinations(expert_cols, 2):
            v = sub[a].notnull() & sub[b].notnull()
            n = int(v.sum())
            if n <= 5:
                continue
            both = int(((sub.loc[v, a] == p) & (sub.loc[v, b] == p)).sum())
            rows_pattern.append({"rater_a": a, "rater_b": b,
                                 "n_overlap": n, "agreement": both / n,
                                 "pattern": p})
    return (pd.concat([pd.DataFrame(rows_overall), pd.DataFrame(rows_pattern)],
                      ignore_index=True)
              .assign(source="Gold Standard Experts"))


def main():
    set_default_style()
    df = load_test_df4()
    dfg = load_experts30()

    # Keep gold-standard rows that also exist in test_df4 (the IRR notebook
    # does the same inner-merge in its cell 6).
    keep = df["filename3"].dropna().unique() if "filename3" in df.columns else None
    if keep is not None:
        dfg = dfg[dfg["file_name"].isin(keep)].copy()

    s = study_expert_pairs(df)
    g = gold_expert_pairs(dfg)
    combined = pd.concat([s, g], ignore_index=True)
    combined.to_csv(ROOT / "figures" / "supp_s5_pairwise.csv", index=False)

    order = ["Overall", "other", "seizure", "lpd", "gpd", "lrda", "grda"]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.violinplot(data=combined, x="pattern", y="agreement", hue="source",
                   split=True, inner="quartile", order=order,
                   palette={"Study Experts": "#7aa9d4",
                            "Gold Standard Experts": "#c66f73"},
                   ax=ax)
    ax.set_xlabel("Pattern")
    ax.set_ylabel("Pairwise agreement")
    ax.set_xticklabels([LABEL_PRETTY.get(p.lower(), p) for p in order])
    ax.set_ylim(0, 1.1)
    fig.suptitle("Pairwise agreement: Study Experts (n=8) vs Gold-Standard Experts (n=30)")
    save_figure(fig, "supp_s5_violin", ROOT / "figures")
    print(f"Wrote figures/supp_s5_violin.{{png,pdf}}")


if __name__ == "__main__":
    main()
