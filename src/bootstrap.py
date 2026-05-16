"""Bootstrap sample-size analysis (Section 2.10, Figure 5).

For each crowd sample size N in 5..50, draw 1000 bootstrap samples of N users
with replacement from the crowd, compute the weighted-majority accuracy of
that sub-crowd on the test set, and report mean + 95% CI of the bootstrap
distribution. Compared against the experts' weighted-majority accuracy.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from tqdm import tqdm

from .scoring import weighted_majority_correct


def expert_weighted_majority_accuracy(df_expert: pd.DataFrame) -> float:
    """Weighted-majority accuracy of the 8 experts on the test set."""
    accs = df_expert.groupby("problem_id").apply(weighted_majority_correct)
    return float(accs.mean())


def crowd_bootstrap_accuracy(df_crowd: pd.DataFrame, sample_size: int,
                             n_bootstrap: int = 1000,
                             rng: np.random.Generator | None = None
                             ) -> tuple[float, tuple[float, float], list[float]]:
    """Bootstrap weighted-majority accuracy for a crowd of size ``sample_size``.

    Returns mean accuracy, (2.5%, 97.5%) percentile CI, and the full vector
    of bootstrap accuracies (so callers can plot the distribution).
    """
    rng = rng or np.random.default_rng()
    user_ids = df_crowd["user_id"].unique()
    # Pre-group for speed: dict[user_id] -> DataFrame slice.
    by_user = {u: g for u, g in df_crowd.groupby("user_id")}

    accs = []
    for _ in range(n_bootstrap):
        sampled = rng.choice(user_ids, size=sample_size, replace=True)
        # Concatenate the chosen users' rows. We don't deduplicate -- repeating
        # a user effectively doubles their vote, which is the standard
        # bootstrap behaviour.
        chunk = pd.concat([by_user[u] for u in sampled], ignore_index=True)
        per_problem = chunk.groupby("problem_id").apply(weighted_majority_correct)
        if len(per_problem):
            accs.append(float(per_problem.mean()))
    lo, hi = np.percentile(accs, [2.5, 97.5])
    return float(np.mean(accs)), (float(lo), float(hi)), accs


def sample_size_curve(df: pd.DataFrame, sizes=range(5, 55, 5),
                      n_bootstrap: int = 1000,
                      seed: int = 0) -> pd.DataFrame:
    """Run the sample-size sweep used for Figure 5.

    Returns a tidy dataframe with columns: sample_size, mean_acc, ci_lower,
    ci_upper. Expert accuracy (a single horizontal reference line in the
    figure) is exposed as ``expert_acc`` attribute on the result for
    convenience.
    """
    rng = np.random.default_rng(seed)

    df_expert = df[df["group"] == "Expert"]
    df_crowd = df[df["group"] == "Crowd"]
    expert_acc = expert_weighted_majority_accuracy(df_expert)

    rows = []
    for size in tqdm(sizes, desc="Sample sizes"):
        mean_acc, (lo, hi), _ = crowd_bootstrap_accuracy(
            df_crowd, sample_size=int(size),
            n_bootstrap=n_bootstrap, rng=rng,
        )
        rows.append({"sample_size": int(size),
                     "mean_acc": mean_acc,
                     "ci_lower": lo, "ci_upper": hi})
    out = pd.DataFrame(rows)
    out.attrs["expert_acc"] = expert_acc
    return out
