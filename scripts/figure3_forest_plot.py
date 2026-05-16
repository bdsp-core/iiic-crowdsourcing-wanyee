"""Figure 3: Forest plot of Crowd - Expert accuracy difference.

Uses the four-model output from src.mixed_models.fit_all_models. The
non-inferiority margin (vertical light-blue line) is at +0.05 because the
plot is in Crowd-Expert orientation: an estimate to the *right* of -0.05
satisfies "Crowd not worse than Expert by more than 5 percentage points".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from src.config import NONINF_MARGIN
from src.data_loading import load_test_df4
from src.mixed_models import fit_all_models
from src.plotting import LABEL_PRETTY, set_default_style, save_figure


def main():
    set_default_style()
    df = load_test_df4()
    ni = fit_all_models(df)["ni_table"]
    ni.to_csv(ROOT / "figures" / "figure3_noninferiority.csv", index=False)

    # Plot order: Overall at top, then SRPPs alphabetically *bottom-up*.
    order = ["Overall"] + sorted([p for p in ni["pattern"].unique() if p != "Overall"])
    y_for_pattern = {p: i for i, p in enumerate(order)}

    fig, ax = plt.subplots(figsize=(8, 5))
    for scoring, color, offset in (("NW", "#1f3a5f", -0.15),
                                   ("WM", "#b22222",  0.15)):
        d = ni[ni["scoring"] == scoring]
        for _, r in d.iterrows():
            y = y_for_pattern[r["pattern"]] + offset
            ax.errorbar(r["diff_crowd_minus_expert"], y,
                        xerr=[[r["diff_crowd_minus_expert"] - r["ci_lower"]],
                              [r["ci_upper"] - r["diff_crowd_minus_expert"]]],
                        fmt="o", color=color, capsize=3, elinewidth=1.2,
                        markersize=6, label=scoring if r["pattern"] == "Overall" else None)
            ax.text(r["diff_crowd_minus_expert"], y + 0.02,
                    f"{r['diff_crowd_minus_expert']:+.2f}",
                    ha="center", fontsize=8)

    ax.axvline(0,                 ls="--", color="#3aaf63", lw=0.8, label="No difference")
    ax.axvline(-NONINF_MARGIN,    ls="--", color="#7ab5e1", lw=0.8, label=f"Non-inferiority (-{NONINF_MARGIN})")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([LABEL_PRETTY.get(p.lower(), p) for p in order])
    ax.invert_yaxis()
    ax.set_xlabel("Crowd − Expert (Negative: Expert better, Positive: Crowd better)")
    ax.set_xlim(-0.4, 0.2)
    # Deduplicate legend entries.
    h, l = ax.get_legend_handles_labels()
    seen, hh, ll = set(), [], []
    for handle, label in zip(h, l):
        if label not in seen:
            seen.add(label)
            hh.append(handle); ll.append(label)
    ax.legend(hh, ll, loc="lower right")
    fig.suptitle("Adjusted accuracy difference: Crowd vs Expert")

    save_figure(fig, "figure3", ROOT / "figures")
    print(f"Wrote figures/figure3.{{png,pdf}}")


if __name__ == "__main__":
    main()
