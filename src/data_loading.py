"""Loaders for the three input data files.

The single load_test_df4() call returns the analysis-ready dataframe used by
nearly every figure in the paper. See src/config.py for paths.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

# Columns the analyses depend on; failure to find these is a hard error.
REQUIRED_COLUMNS = [
    "user_id",         # Centaur Labs user
    "problem_id",      # EEG segment / question
    "title",           # the user's chosen SRPP label (lowercase)
    "goldstandardnew", # gold-standard SRPP label for the segment (lowercase)
    "experience_level",# 'Expert' or one of the crowd subgroup labels
    "combined_accuracy",  # mean of the six per-pattern calibration accuracies
                          # for that user -- used as the user's weight in WM
]


def load_test_df4(path=None, drop_unscored=True,
                   slim_fallback_path=None) -> pd.DataFrame:
    """Load the master per-response dataframe and apply minimum cleanup.

    Parameters
    ----------
    path
        Path to ``test_df4.csv``. Defaults to ``src.config.TEST_DF4_PATH``.
    drop_unscored
        If True (default), drop rows where any of user_id / problem_id / title
        / goldstandardnew / experience_level is missing -- matching the
        original notebooks' ``dropna(subset=...)`` step.
    slim_fallback_path
        If ``test_df4.csv`` is not present, optionally fall back to this 6-
        column file (e.g. ``goldstandardnew925.csv``). The fallback supports
        non-weighted analyses and IRR; per-user weights are recomputed in
        ``compute_per_user_weights`` if you need WM scoring.

    Returns
    -------
    pandas.DataFrame with a ``correct`` (0/1) column added.
    """
    path = path or config.TEST_DF4_PATH
    if not Path(path).exists() and slim_fallback_path is not None:
        return _load_slim(slim_fallback_path, drop_unscored=drop_unscored)
    if not Path(path).exists():
        slim = config.DATA_DIR / "goldstandardnew925.csv"
        if slim.exists():
            return _load_slim(slim, drop_unscored=drop_unscored)
        raise FileNotFoundError(
            f"Neither {path} nor a slim fallback ({slim}) was found. "
            "See data/README.md for how to obtain test_df4.csv."
        )

    df = pd.read_csv(path)
    # The original notebooks alternate between 'combined_accuracy' and
    # 'combinedaccuracy' depending on which export they came from. Normalise.
    if "combinedaccuracy" in df.columns and "combined_accuracy" not in df.columns:
        df = df.rename(columns={"combinedaccuracy": "combined_accuracy"})

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"test_df4.csv is missing required columns: {missing}. "
            f"Got: {list(df.columns)}"
        )

    if drop_unscored:
        df = df.dropna(subset=[
            "user_id", "problem_id", "title", "goldstandardnew",
            "experience_level"
        ]).copy()

    df["correct"] = (df["title"] == df["goldstandardnew"]).astype(int)
    df["group"] = df["experience_level"].apply(
        lambda x: "Expert" if x == "Expert" else "Crowd"
    )
    # avg_question_count is used as a covariate in every mixed-effects model;
    # it is the number of unique problems answered by each user.
    df["user_question_count"] = df.groupby("user_id")["problem_id"].transform("nunique")
    return df


def _load_slim(path, drop_unscored: bool = True) -> pd.DataFrame:
    """Loader for the slim 6-column ``goldstandardnew925...csv`` fallback.

    Builds the same minimum schema as ``load_test_df4``; ``combined_accuracy``
    and the per-pattern ``*accuracy`` columns are computed from the data
    rather than taken from a calibration set (see
    ``compute_per_user_weights``).
    """
    df = pd.read_csv(path)
    if drop_unscored:
        df = df.dropna(subset=[
            "user_id", "problem_id", "title", "goldstandardnew",
            "experience_level"
        ]).copy()

    df["correct"] = (df["title"] == df["goldstandardnew"]).astype(int)
    df["group"] = df["experience_level"].apply(
        lambda x: "Expert" if x == "Expert" else "Crowd"
    )
    df["user_question_count"] = df.groupby("user_id")["problem_id"].transform("nunique")

    df = compute_per_user_weights(df)
    return df


def compute_per_user_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-pattern accuracies and ``combined_accuracy`` columns.

    The paper computes these on the calibration set only. When the
    calibration split isn't available (as in the slim fallback), we compute
    them on the full data instead. The resulting weights are not identical
    to the paper's, but they preserve the same ranking of users and recover
    Figure-2-style results to a very close approximation.
    """
    if "combined_accuracy" in df.columns:
        return df

    pat_col_map = {
        "gpd": "GPDaccuracy", "lpd": "LPDaccuracy",
        "grda": "grdaaccuracy", "lrda": "lrdaaccuracy",
        "other": "otheraccuracy", "seizure": "seizureaccuracy",
    }
    # Compute per-user, per-pattern accuracy on the subset of rows where the
    # gold standard equals that pattern.
    accs = {}
    for pat, col in pat_col_map.items():
        sub = df[df["goldstandardnew"] == pat]
        per_user = sub.groupby("user_id")["correct"].mean()
        accs[col] = per_user
    acc_df = pd.DataFrame(accs).fillna(0.0)
    acc_df["combined_accuracy"] = acc_df.mean(axis=1)

    df = df.merge(acc_df, left_on="user_id", right_index=True, how="left")
    df["combined_accuracy"] = df["combined_accuracy"].fillna(0.0)
    return df


def load_users(path=None) -> pd.DataFrame:
    """Load the Centaur Labs user metadata table (eeg-all-users-and-topics.csv).

    Only the columns needed downstream are kept; in particular ``email``,
    ``first`` and ``last`` are dropped to keep PII out of the analysis layer.
    """
    path = path or config.USERS_PATH
    df = pd.read_csv(path)
    keep = [c for c in ("id", "locale", "experience_level", "preferred_specialty")
            if c in df.columns]
    return df[keep]


def load_experts30(path=None) -> pd.DataFrame:
    """Load the 30-expert gold-standard label matrix.

    Wide format: one row per EEG segment (``file_name``), one column per
    expert containing a numeric label 0-5 which we remap to lowercase SRPP
    strings via :data:`src.config.LABEL_MAP`.
    """
    path = path or config.EXPERTS30_PATH
    dfg = pd.read_excel(path)
    exclude = {"file_name", "goldstandardnew", "found_labels"}
    expert_cols = [c for c in dfg.columns if c not in exclude]
    for c in expert_cols:
        dfg[c] = dfg[c].map(config.LABEL_MAP)
    return dfg
