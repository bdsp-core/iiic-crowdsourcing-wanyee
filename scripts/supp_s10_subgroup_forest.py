"""Supplemental S10: forest plot of adjusted Crowd - Expert difference by subgroup.

For each crowd subgroup g (Section 2.8 / src.config.CROWD_SUBGROUPS) and each
SRPP we fit::

    accuracy ~ subgroup + avg_question_count + (1 | problem_id)

restricted to Expert rows + Crowd-subset-g rows. The fixed effect on
``subgroup[T.Expert]`` gives (Expert - Crowd_g); we negate to (Crowd - Expert)
and plot with 95% CIs and Bonferroni-adjusted significance markers.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

from src.config import CROWD_SUBGROUPS, SRPPS
from src.data_loading import load_test_df4
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def fit_one(df: pd.DataFrame, subgroup_levels: list[str], pattern: str | None):
    """Return (estimate, se) for (Crowd_g - Expert) on the given pattern."""
    sub = df.copy()
    if pattern:
        sub = sub[sub["goldstandardnew"] == pattern]
    sub = sub[(sub["group"] == "Expert") |
              (sub["experience_level"].isin(subgroup_levels))]
    if sub.empty or sub["group"].nunique() < 2:
        return float("nan"), float("nan")

    sub["subgroup"] = np.where(sub["group"] == "Expert", "Expert", "Crowd")
    agg = sub.groupby(["problem_id", "subgroup"]).agg(
        accuracy=("correct", "mean"),
        avg_question_count=("user_question_count", "mean"),
    ).reset_index()
    agg["subgroup"] = agg["subgroup"].astype("category")
    try:
        res = smf.mixedlm("accuracy ~ subgroup + avg_question_count",
                          agg, groups=agg["problem_id"]).fit()
    except Exception:
        return float("nan"), float("nan")
    coef = res.params.get("subgroup[T.Expert]", float("nan"))
    se = float(np.sqrt(res.cov_params().loc["subgroup[T.Expert]",
                                            "subgroup[T.Expert]"]))
    # Coefficient is (Expert - Crowd_g); we want (Crowd_g - Expert).
    return -coef, se


def main():
    set_default_style()
    df = load_test_df4()

    rows = []
    n_tests = len(CROWD_SUBGROUPS) * (len(SRPPS) + 1)  # subgroups x (Overall + 6 SRPPs)
    for sg_label, sg_levels in CROWD_SUBGROUPS.items():
        for pat in ["Overall"] + SRPPS:
            est, se = fit_one(df, sg_levels, pat if pat != "Overall" else None)
            rows.append({"subgroup": sg_label, "pattern": pat,
                         "estimate": est, "se": se,
                         "ci_lo": est - 1.96 * se if not np.isnan(se) else float("nan"),
                         "ci_hi": est + 1.96 * se if not np.isnan(se) else float("nan")})
    out = pd.DataFrame(rows)
    # Two-sided p-values for "different from 0"; Bonferroni across all tests.
    from scipy.stats import norm
    out["p_two_sided"] = 2 * (1 - norm.cdf(np.abs(out["estimate"] / out["se"])))
    out["p_bonf"] = (out["p_two_sided"] * n_tests).clip(upper=1.0)
    out.to_csv(ROOT / "figures" / "supp_s10_subgroup_forest.csv", index=False)

    # Plot.
    patterns_order = ["Overall"] + SRPPS
    subgroups_order = list(CROWD_SUBGROUPS.keys())
    n_p = len(patterns_order)

    fig, ax = plt.subplots(figsize=(8, 1 + 0.6 * len(out)))
    y = 0
    yticks, yticklabels = [], []
    for sg in subgroups_order:
        for pat in patterns_order:
            r = out.loc[(out["subgroup"] == sg) & (out["pattern"] == pat)].iloc[0]
            color = "#b22222" if r["p_bonf"] < 0.05 else "#1f3a5f"
            ax.errorbar(r["estimate"], y,
                        xerr=[[r["estimate"] - r["ci_lo"]],
                              [r["ci_hi"] - r["estimate"]]],
                        fmt="s", color=color, markersize=4, capsize=2)
            yticks.append(y)
            yticklabels.append(f"{sg} / {LABEL_PRETTY.get(pat.lower(), pat)}")
            y += 1
    ax.axvline(0, ls="--", color="0.4", lw=0.7)
    ax.set_yticks(yticks); ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()
    ax.set_xlabel("Crowd_subgroup − Expert (red: Bonferroni-adjusted p < 0.05)")
    fig.suptitle("Supp S10: Adjusted Crowd-subgroup minus Expert by SRPP")
    fig.tight_layout()
    save_figure(fig, "supp_s10_subgroup_forest", ROOT / "figures")
    print("Wrote figures/supp_s10_subgroup_forest.{png,pdf}")


if __name__ == "__main__":
    main()
