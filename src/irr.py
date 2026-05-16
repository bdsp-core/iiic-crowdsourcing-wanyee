"""Inter-rater agreement metrics: pairwise agreement, Fleiss' kappa, Gwet's AC1.

These reproduce the IRR analyses in Section 2.2 of the paper and Supplementals
S4 and S5. The Fleiss / Gwet implementations follow the standard definitions:

  * pairwise agreement (PA) = mean over rater pairs of (# agreed / # overlap),
    restricted to pairs with at least ``min_overlap`` shared items.
  * Fleiss' kappa = (Pa - Pe(F)) / (1 - Pe(F)) where Pa is the mean item-level
    agreement and Pe(F) is the expected agreement under category-distribution
    independence.
  * Gwet's AC1 = (Pa - Pe(G)) / (1 - Pe(G)) where Pe(G) = sum_k pk*(1-pk)/(K-1)
    and K is the number of categories. AC1 is less sensitive than kappa to
    skewed category prevalences (Wongpakaran 2013; cited as ref 18 in the paper).
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Long-format pairwise agreement (used for the 8 study experts in test_df4)
# ---------------------------------------------------------------------------

def pairwise_overall(df: pd.DataFrame,
                     id_col: str = "user_id",
                     item_col: str = "problem_id",
                     answer_col: str = "title",
                     min_overlap: int = 5) -> pd.DataFrame:
    """Return one row per rater pair: overall fraction-agreement.

    Pairs with fewer than ``min_overlap`` shared items are kept but flagged
    via the ``Total Overlaps`` column; callers usually filter with > 5.
    """
    rows = []
    raters = sorted(df[id_col].unique().tolist())
    for a, b in combinations(raters, 2):
        # Pivot once per pair using a merge -- much faster than the naive
        # double-groupby loop in the original notebook for many raters.
        da = df.loc[df[id_col] == a, [item_col, answer_col]].drop_duplicates(item_col)
        db = df.loc[df[id_col] == b, [item_col, answer_col]].drop_duplicates(item_col)
        merged = da.merge(db, on=item_col, suffixes=("_a", "_b"))
        n = len(merged)
        if n == 0:
            continue
        agree = (merged[f"{answer_col}_a"] == merged[f"{answer_col}_b"]).sum()
        rows.append({
            "rater_a": a, "rater_b": b,
            "n_overlap": n, "n_agree": int(agree),
            "agreement": agree / n,
        })
    out = pd.DataFrame(rows)
    return out[out["n_overlap"] > min_overlap].copy() if not out.empty else out


def pairwise_by_pattern(df: pd.DataFrame,
                        gold_col: str = "goldstandardnew",
                        id_col: str = "user_id",
                        item_col: str = "problem_id",
                        answer_col: str = "title",
                        patterns=("gpd", "grda", "lpd", "lrda", "other", "seizure"),
                        min_overlap: int = 5) -> pd.DataFrame:
    """Per-pattern pairwise agreement.

    For each pattern p we restrict to items whose gold standard is p, then
    compute, for each pair of raters with overlap on those items, the
    fraction of shared items where BOTH raters answered p. This matches the
    notebook's behaviour and what the paper reports in Section 3.2.
    """
    out_frames = []
    for p in patterns:
        sub = df[df[gold_col] == p]
        if sub.empty:
            continue
        pa = pairwise_overall(sub, id_col=id_col, item_col=item_col,
                              answer_col=answer_col, min_overlap=min_overlap)
        if pa.empty:
            continue
        # Replace 'agreement' with "both answered the pattern" agreement.
        rows = []
        raters = sorted(sub[id_col].unique().tolist())
        for a, b in combinations(raters, 2):
            da = sub.loc[sub[id_col] == a, [item_col, answer_col]].drop_duplicates(item_col)
            db = sub.loc[sub[id_col] == b, [item_col, answer_col]].drop_duplicates(item_col)
            m = da.merge(db, on=item_col, suffixes=("_a", "_b"))
            n = len(m)
            if n <= min_overlap:
                continue
            both = ((m[f"{answer_col}_a"] == p) & (m[f"{answer_col}_b"] == p)).sum()
            rows.append({
                "rater_a": a, "rater_b": b, "pattern": p,
                "n_overlap": n, "n_both": int(both),
                "agreement": both / n,
            })
        out_frames.append(pd.DataFrame(rows))
    return pd.concat(out_frames, ignore_index=True) if out_frames else pd.DataFrame()


# ---------------------------------------------------------------------------
# Wide-format Fleiss kappa & Gwet AC1 (used for the 30 gold-standard experts
# in labels_experts30.xlsx, and also for the 8 study experts after pivoting).
# ---------------------------------------------------------------------------

def _item_rating_counts(ratings: pd.DataFrame, categories) -> np.ndarray:
    """Return an (n_items, n_categories) array of category counts per item.

    ``ratings`` is wide-format: rows = items, columns = raters, values = category.
    NaN cells are treated as 'rater did not score'.
    """
    n_items = len(ratings)
    n_cat = len(categories)
    counts = np.zeros((n_items, n_cat), dtype=float)
    for j, c in enumerate(categories):
        counts[:, j] = (ratings == c).sum(axis=1).values
    return counts


def fleiss_kappa(ratings: pd.DataFrame, categories=None) -> dict:
    """Compute Fleiss' kappa allowing variable raters per item.

    Returns a dict with keys: pa (observed agreement), pe (expected),
    kappa, n_items, n_categories.
    """
    if categories is None:
        categories = sorted(pd.unique(ratings.values.ravel()))
        categories = [c for c in categories if pd.notna(c)]
    counts = _item_rating_counts(ratings, categories)
    n_per_item = counts.sum(axis=1)
    valid = n_per_item > 1
    counts = counts[valid]
    n_per_item = n_per_item[valid]

    # Per-item agreement (Fleiss eq.):
    #   P_i = (1 / (n_i*(n_i-1))) * sum_j n_ij*(n_ij-1)
    p_i = ((counts * (counts - 1)).sum(axis=1)) / (n_per_item * (n_per_item - 1))
    pa = float(p_i.mean())

    # Category marginal probabilities:
    p_j = counts.sum(axis=0) / counts.sum()
    pe = float((p_j ** 2).sum())

    kappa = (pa - pe) / (1 - pe) if (1 - pe) != 0 else float("nan")
    return {"pa": pa, "pe": pe, "kappa": kappa,
            "n_items": int(valid.sum()), "n_categories": len(categories)}


def gwet_ac1(ratings: pd.DataFrame, categories=None) -> dict:
    """Compute Gwet's AC1 (Gwet 2008; Wongpakaran 2013)."""
    if categories is None:
        categories = sorted(pd.unique(ratings.values.ravel()))
        categories = [c for c in categories if pd.notna(c)]
    K = len(categories)
    counts = _item_rating_counts(ratings, categories)
    n_per_item = counts.sum(axis=1)
    valid = n_per_item > 1
    counts = counts[valid]
    n_per_item = n_per_item[valid]

    p_i = ((counts * (counts - 1)).sum(axis=1)) / (n_per_item * (n_per_item - 1))
    pa = float(p_i.mean())

    pi_k = counts.sum(axis=0) / counts.sum()
    pe = float((pi_k * (1 - pi_k)).sum() / (K - 1)) if K > 1 else float("nan")
    ac1 = (pa - pe) / (1 - pe) if (1 - pe) != 0 else float("nan")
    return {"pa": pa, "pe": pe, "ac1": ac1,
            "n_items": int(valid.sum()), "n_categories": K}


def long_to_wide(df: pd.DataFrame,
                 item_col: str = "problem_id",
                 rater_col: str = "user_id",
                 answer_col: str = "title") -> pd.DataFrame:
    """Pivot a long-format reads table into items x raters wide format."""
    wide = df.pivot_table(index=item_col, columns=rater_col,
                          values=answer_col, aggfunc="first")
    return wide


def irr_metrics_by_pattern(wide_ratings: pd.DataFrame,
                           gold_col: str = "goldstandardnew",
                           categories=None) -> pd.DataFrame:
    """Compute PA / Fleiss / Gwet for Overall + each pattern.

    ``wide_ratings`` has a ``goldstandardnew`` column plus one column per
    rater containing the rater's label (lowercase SRPP string or NaN).
    """
    rater_cols = [c for c in wide_ratings.columns if c != gold_col]
    rows = []

    overall = wide_ratings[rater_cols]
    fk = fleiss_kappa(overall, categories=categories)
    ac = gwet_ac1(overall, categories=categories)
    rows.append({"pattern": "Overall",
                 "pa": fk["pa"], "fleiss_kappa": fk["kappa"], "fleiss_pe": fk["pe"],
                 "gwet_ac1": ac["ac1"], "gwet_pe": ac["pe"],
                 "n_items": fk["n_items"]})

    for p in sorted(wide_ratings[gold_col].dropna().unique()):
        sub = wide_ratings.loc[wide_ratings[gold_col] == p, rater_cols]
        if sub.empty:
            continue
        fk = fleiss_kappa(sub, categories=categories)
        ac = gwet_ac1(sub, categories=categories)
        rows.append({"pattern": p,
                     "pa": fk["pa"], "fleiss_kappa": fk["kappa"], "fleiss_pe": fk["pe"],
                     "gwet_ac1": ac["ac1"], "gwet_pe": ac["pe"],
                     "n_items": fk["n_items"]})
    return pd.DataFrame(rows)
