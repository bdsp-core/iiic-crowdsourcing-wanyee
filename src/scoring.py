"""Weighted-majority voting and accuracy helpers (Section 2.5 of the paper).

Each user i has a weight w_i = mean of their six per-pattern calibration
accuracies. For a given question j and a set of voters, the weighted majority
prediction is::

    argmax_{c in C}  sum_{i} w_i * I(c_{i,j} = c)

where C is the set of SRPP labels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_majority_predict(sub_df: pd.DataFrame,
                              weight_col: str = "combined_accuracy",
                              answer_col: str = "title") -> str:
    """Weighted majority vote across the rows of one (problem, group) slice."""
    return sub_df.groupby(answer_col)[weight_col].sum().idxmax()


def weighted_majority_correct(sub_df: pd.DataFrame,
                              weight_col: str = "combined_accuracy",
                              answer_col: str = "title",
                              gold_col: str = "goldstandardnew") -> int:
    """1 if the weighted-majority vote matches the gold standard, else 0."""
    pred = weighted_majority_predict(sub_df, weight_col, answer_col)
    return int(pred == sub_df[gold_col].iloc[0])


def per_problem_aggregates(df: pd.DataFrame,
                           group_cols=("problem_id", "group"),
                           pattern_col: str | None = None) -> pd.DataFrame:
    """Build the per-(problem, group [, pattern]) table used by mixed models.

    Returns a long dataframe with columns:
      problem_id, group [, pattern], accuracy, weighted_accuracy,
      avg_question_count, n.

    ``accuracy`` is the non-weighted mean of ``correct`` across that group's
    raters on that problem (Section 2.4); ``weighted_accuracy`` is the
    weighted-majority correctness for the group on that problem (Section 2.5).
    """
    keys = list(group_cols) + ([pattern_col] if pattern_col else [])

    rows = []
    for key_vals, sub in df.groupby(keys, observed=True):
        rec = dict(zip(keys, key_vals if isinstance(key_vals, tuple) else (key_vals,)))
        rec["accuracy"] = sub["correct"].mean()
        rec["weighted_accuracy"] = weighted_majority_correct(sub)
        rec["avg_question_count"] = sub["user_question_count"].mean()
        rec["n"] = len(sub)
        rows.append(rec)
    return pd.DataFrame(rows)
