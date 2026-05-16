"""Mixed-effects models 1-4 and the non-inferiority tests (Sections 2.4-2.5).

Two model families are fit, each in two forms:

  * Non-Weighted (NW): outcome = per-(problem, group) mean correctness.
  * Weighted Majority (WM): outcome = per-(problem, group) weighted-majority
    correctness (0 or 1).

For each family we fit:

  * Model 1 / 3 (Overall):  outcome ~ group + avg_question_count
  * Model 2 / 4 (By-pattern): outcome ~ group * pattern + avg_question_count

All four models include a random intercept for problem_id to capture between-
problem variability (Section 2.4).

The non-inferiority test (margin = 0.05; Bonferroni p < 0.025 per pattern)
asks whether Expert - Crowd is less than the margin, i.e. whether the crowd
is non-inferior to the experts.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm

from . import config


# ---------------------------------------------------------------------------
# Model fitting
# ---------------------------------------------------------------------------

def fit_overall(agg: pd.DataFrame, outcome: str):
    """Fit an overall (no by-pattern interaction) mixed model."""
    model = smf.mixedlm(
        f"{outcome} ~ group + avg_question_count",
        agg,
        groups=agg["problem_id"],
    )
    return model.fit()


def fit_by_pattern(agg: pd.DataFrame, outcome: str):
    """Fit a by-pattern mixed model with group * pattern interaction."""
    model = smf.mixedlm(
        f"{outcome} ~ group * pattern + avg_question_count",
        agg,
        groups=agg["problem_id"],
    )
    return model.fit()


# ---------------------------------------------------------------------------
# Non-inferiority test
# ---------------------------------------------------------------------------

@dataclass
class NonInfResult:
    """Container for one non-inferiority test result."""
    pattern: str           # 'Overall' or one of the 6 SRPPs
    scoring: str           # 'NW' or 'WM'
    diff_crowd_minus_expert: float
    se: float
    ci_lower: float        # 95% CI on (Crowd - Expert)
    ci_upper: float
    z: float
    p_one_sided: float


def _ci(estimate, se, z=1.96):
    return estimate - z * se, estimate + z * se


def overall_noninf(result, scoring: str) -> NonInfResult:
    """Extract Crowd - Expert non-inferiority test from an Overall model.

    Statsmodels parameterises ``group`` with Crowd as the reference category,
    so the fitted coefficient on ``group[T.Expert]`` is (Expert - Crowd). We
    negate it to express the result as (Crowd - Expert), the form used in the
    paper's forest plots (Fig 3, Supp S10).
    """
    coef = result.params["group[T.Expert]"]
    se = float(np.sqrt(result.cov_params().loc["group[T.Expert]", "group[T.Expert]"]))

    expert_minus_crowd = coef
    crowd_minus_expert = -expert_minus_crowd
    # 95% CI on (Crowd - Expert)
    lo, hi = _ci(expert_minus_crowd, se)
    ci_lower, ci_upper = -hi, -lo

    # Non-inferiority of Crowd vs Expert (margin = 0.05):
    #   H0: Expert - Crowd > 0.05   ;   H1: Expert - Crowd < 0.05
    # z = (Expert - Crowd - margin) / SE   (one-sided, reject for small z)
    z = (expert_minus_crowd - config.NONINF_MARGIN) / se
    p = float(norm.cdf(z))

    return NonInfResult("Overall", scoring, crowd_minus_expert, se,
                        ci_lower, ci_upper, z, p)


def by_pattern_noninf(result, patterns: list[str], scoring: str
                      ) -> list[NonInfResult]:
    """Extract per-pattern non-inferiority tests from a by-pattern model.

    The model is fit with the first pattern (alphabetical: 'gpd') as the
    reference, so the per-pattern Expert-Crowd contrast for a non-reference
    pattern ``p`` is ``group[T.Expert] + group[T.Expert]:pattern[T.p]``, and
    its variance is computed via the contrast vector.
    """
    out: list[NonInfResult] = []

    base_coef = "group[T.Expert]"
    params = result.params
    cov = result.cov_params()

    # Reference pattern (the one *without* an interaction term) is the
    # alphabetically first; statsmodels makes this the baseline of the
    # categorical 'pattern'.
    ref_pattern = sorted(patterns)[0]

    # Reference pattern: just group[T.Expert] = Expert - Crowd at that pattern.
    coef = params[base_coef]
    se = float(np.sqrt(cov.loc[base_coef, base_coef]))
    crowd_minus_expert = -coef
    lo, hi = _ci(coef, se)
    ci_l, ci_u = -hi, -lo
    z = (coef - config.NONINF_MARGIN) / se
    out.append(NonInfResult(ref_pattern, scoring, crowd_minus_expert, se,
                            ci_l, ci_u, z, float(norm.cdf(z))))

    # Other patterns: contrast (group[T.Expert] + interaction).
    for p in patterns:
        if p == ref_pattern:
            continue
        inter = f"group[T.Expert]:pattern[T.{p}]"
        if inter not in params.index:
            continue  # pattern absent for some reason
        # Linear combination vector L: 1 on base_coef, 1 on inter, 0 elsewhere.
        contrast = pd.Series(0.0, index=params.index)
        contrast[base_coef] = 1.0
        contrast[inter] = 1.0
        diff_expert_minus_crowd = float(contrast @ params)
        var = float(contrast @ cov @ contrast)
        se = float(np.sqrt(var))
        crowd_minus_expert = -diff_expert_minus_crowd
        lo, hi = _ci(diff_expert_minus_crowd, se)
        ci_l, ci_u = -hi, -lo
        z = (diff_expert_minus_crowd - config.NONINF_MARGIN) / se
        out.append(NonInfResult(p, scoring, crowd_minus_expert, se,
                                ci_l, ci_u, z, float(norm.cdf(z))))
    return out


# ---------------------------------------------------------------------------
# Convenience wrapper: fit all four models and return predictions + NI table
# ---------------------------------------------------------------------------

def fit_all_models(df: pd.DataFrame) -> dict:
    """Fit Models 1-4 on the standardised dataframe and return a dict.

    Returns
    -------
    dict with keys:
      'agg_overall_NW', 'agg_overall_WM', 'agg_pattern_NW', 'agg_pattern_WM'
          The per-(problem, group [, pattern]) aggregates, each with a
          ``predicted_accuracy`` column populated from the fitted model.
      'result_overall_NW', 'result_overall_WM',
      'result_pattern_NW', 'result_pattern_WM'
          The four statsmodels results objects.
      'ni_table': pandas.DataFrame
          Tidy table of non-inferiority results for Overall + each SRPP,
          for both NW and WM scoring (columns: pattern, scoring,
          diff_crowd_minus_expert, se, ci_lower, ci_upper, z, p_one_sided,
          p_bonf).
    """
    from .scoring import per_problem_aggregates

    # Aggregates.
    agg_o_nw = per_problem_aggregates(df, group_cols=("problem_id", "group"))
    agg_o_wm = agg_o_nw.copy()   # same rows, just use different outcome col.

    agg_p_nw = per_problem_aggregates(
        df, group_cols=("problem_id", "group"), pattern_col="goldstandardnew"
    ).rename(columns={"goldstandardnew": "pattern"})
    agg_p_wm = agg_p_nw.copy()

    # Fit.
    res_o_nw = fit_overall(agg_o_nw, outcome="accuracy")
    res_o_wm = fit_overall(agg_o_wm, outcome="weighted_accuracy")
    res_p_nw = fit_by_pattern(agg_p_nw, outcome="accuracy")
    res_p_wm = fit_by_pattern(agg_p_wm, outcome="weighted_accuracy")

    # Predictions.
    agg_o_nw["predicted_accuracy"] = res_o_nw.predict(agg_o_nw)
    agg_o_wm["predicted_accuracy"] = res_o_wm.predict(agg_o_wm)
    agg_p_nw["predicted_accuracy"] = res_p_nw.predict(agg_p_nw)
    agg_p_wm["predicted_accuracy"] = res_p_wm.predict(agg_p_wm)

    # Non-inferiority table.
    patterns = sorted(agg_p_nw["pattern"].dropna().unique().tolist())
    ni_rows: list[NonInfResult] = []
    ni_rows.append(overall_noninf(res_o_nw, "NW"))
    ni_rows.append(overall_noninf(res_o_wm, "WM"))
    ni_rows += by_pattern_noninf(res_p_nw, patterns, "NW")
    ni_rows += by_pattern_noninf(res_p_wm, patterns, "WM")
    ni_df = pd.DataFrame([r.__dict__ for r in ni_rows])
    # Bonferroni adjust per-pattern (6 tests).
    is_overall = ni_df["pattern"] == "Overall"
    ni_df["p_bonf"] = ni_df["p_one_sided"]
    ni_df.loc[~is_overall, "p_bonf"] = (
        ni_df.loc[~is_overall, "p_one_sided"] * len(patterns)
    ).clip(upper=1.0)

    return dict(
        agg_overall_NW=agg_o_nw, agg_overall_WM=agg_o_wm,
        agg_pattern_NW=agg_p_nw, agg_pattern_WM=agg_p_wm,
        result_overall_NW=res_o_nw, result_overall_WM=res_o_wm,
        result_pattern_NW=res_p_nw, result_pattern_WM=res_p_wm,
        ni_table=ni_df,
    )
