"""Build ``test_df4.csv`` from the upstream Centaur Labs exports.

Reproduces the merge pipeline that Wan-Yee originally implemented in
``notebooks_original/build_test_df4.ipynb``. Reads four upstream files,
joins them on the documented keys, derives ``goldstandardnew`` from
either the 30-expert vote argmax (when available, via the slim
``goldstandardnew925.csv``) or Centaur's stored ``Correct Label``, applies
the per-user calibration/test eligibility filter (Section 2.3 of the
paper), and computes per-user / per-pattern accuracies on the calibration
subset for use as weighted-majority weights.

Input files expected in ``data/``:
  1251-all-reads_ac.csv                  -- per-read responses (657k rows)
  Results_SeizureLike_Patterns_..csv     -- per-question Centaur summary
                                            (we keep it as data/centaur_summary.csv)
  1251-all-users_demo_info.csv           -- experience_level, preferred_specialty
  eeg-all-users-and-topics.csv           -- locale (for Supp S1 country mapping)
  goldstandardnew925.csv                 -- Wan-Yee's slim intermediate file,
                                            used as the source for ``goldstandardnew``
                                            and the manual ``experience_level=Expert``
                                            tagging of the 8 study experts.

Output:
  staging/annotations/test_df4.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from src.data_loading import apply_calibration_eligibility_filter

DATA = ROOT / "data"
OUT = ROOT / "staging" / "annotations" / "test_df4.csv"


SRPP = ("gpd", "grda", "lpd", "lrda", "other", "seizure")


def _strip_quotes(s):
    if isinstance(s, str):
        return s.strip("'\"")
    return s


def main():
    # ---------------------------------------------------------------- reads
    print("Loading 1251-all-reads_ac.csv …")
    reads = pd.read_csv(DATA / "1251-all-reads_ac.csv", low_memory=False)
    reads["title"] = reads["title"].str.lower()
    print(f"  {len(reads):,} rows")

    # ----------------------------------------------------------- centaur summary
    print("Loading Centaur summary (per-question)…")
    summary = pd.read_csv(DATA / "centaur_summary.csv", low_memory=False)
    summary.columns = summary.columns.str.replace("﻿", "", regex=False)
    # Trim quotes from labels (Centaur exports stored them as 'seizure' etc.)
    summary["Correct Label"] = summary["Correct Label"].apply(_strip_quotes).str.lower()
    keep = summary[["Case ID", "Origin", "Correct Label", "Qualified Reads"]]
    print(f"  {len(keep):,} unique questions")

    # ------------------------------------------------------------ user demo
    print("Loading user demographics + locale …")
    demo = pd.read_csv(DATA / "1251-all-users_demo_info.csv", low_memory=False)
    demo = demo[["id", "country", "experience_level", "preferred_specialty"]]

    users = pd.read_csv(DATA / "eeg-all-users-and-topics.csv", low_memory=False,
                        usecols=["id", "locale"])

    # --------------------------------------------------- slim CSV (gold std)
    print("Loading goldstandardnew925.csv (slim gold-standard CSV) …")
    slim = pd.read_csv(DATA / "goldstandardnew925.csv")
    slim["title"] = slim["title"].str.lower()
    slim["goldstandardnew"] = slim["goldstandardnew"].str.lower()
    # Per-(problem_id) gold standard derived previously by Wan-Yee.
    gs_per_problem = (slim.drop_duplicates("problem_id")
                          .set_index("problem_id")["goldstandardnew"])
    # The 8 study experts: user_ids that the slim file tagged as Expert.
    expert_user_ids = set(slim.loc[slim["experience_level"] == "Expert",
                                   "user_id"].unique())
    print(f"  goldstandardnew known for {len(gs_per_problem):,} problems")
    print(f"  manual Expert-tag set: {len(expert_user_ids)} users")

    # --------------------------------------------------------------- merge
    print("\nMerging …")
    df = reads.merge(keep, left_on="problem_id", right_on="Case ID", how="left")
    df = df.merge(demo, left_on="user_id", right_on="id",
                  suffixes=("", "_demo"), how="left")
    df = df.merge(users, left_on="user_id", right_on="id",
                  suffixes=("", "_topics"), how="left")

    # ------------------------------------- goldstandardnew (max ∨ Correct)
    df["goldstandardnew_from_slim"] = df["problem_id"].map(gs_per_problem)
    df["goldstandardnew"] = df["goldstandardnew_from_slim"].combine_first(
        df["Correct Label"]
    )
    n_from_slim = df["goldstandardnew_from_slim"].notna().sum()
    n_from_centaur = df["goldstandardnew"].notna().sum() - n_from_slim
    n_missing = df["goldstandardnew"].isna().sum()
    print(f"  goldstandardnew sources: "
          f"{n_from_slim:,} from slim (vote-argmax), "
          f"{n_from_centaur:,} from Centaur Correct Label, "
          f"{n_missing:,} missing")

    # --------------------------------------- manual Expert override
    df.loc[df["user_id"].isin(expert_user_ids), "experience_level"] = "Expert"

    # ------------- derive segment_id (matchfile stem) for downstream lookups
    df["matchfile"] = df["Origin"]
    df["filename3"] = (df["Origin"].astype(str)
                       .str.extract(r"/([^/]+)\.png$", expand=False)
                       .str.replace(" copy", "", regex=False))
    # Apply the same Centaur S3 prefix Wan-Yee's CSV uses, so downstream
    # code that follows ``matchfile`` still works.
    label_dir = df["goldstandardnew"].str.upper()
    df["matchfile"] = (
        "https://centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/"
        + label_dir.fillna("Other")
        + "/" + df["filename3"].fillna("UNKNOWN") + ".png"
    )

    # -------------------------------- drop rows missing the required scoring
    before = len(df)
    df = df.dropna(subset=["user_id", "problem_id", "title",
                            "goldstandardnew", "experience_level"]).copy()
    print(f"  Dropped {before - len(df):,} rows missing required scoring "
          f"({len(df):,} retained)")

    # ----------------------- correctness flag + Crowd/Expert grouping
    df["correct"] = (df["title"] == df["goldstandardnew"]).astype(int)
    df["group"] = np.where(df["experience_level"] == "Expert", "Expert", "Crowd")

    # --------------------------- eligibility filter (§2.3, greedy set cover)
    print("\nApplying calibration-eligibility filter …")
    df = apply_calibration_eligibility_filter(df)
    n_users = df["user_id"].nunique()
    n_calib = df["in_calibration"].sum()
    n_test = (~df["in_calibration"]).sum()
    print(f"  qualified users: {n_users:,}")
    print(f"  calibration rows: {n_calib:,}")
    print(f"  test rows: {n_test:,}")

    # ---------- per-user / per-pattern accuracy on CALIBRATION rows only
    print("\nComputing per-user calibration accuracies …")
    calib = df[df["in_calibration"]]
    pat_col_map = {
        "gpd": "GPDaccuracy", "lpd": "LPDaccuracy",
        "grda": "grdaaccuracy", "lrda": "lrdaaccuracy",
        "other": "otheraccuracy", "seizure": "seizureaccuracy",
    }
    accs = {}
    for pat, col in pat_col_map.items():
        sub = calib[calib["goldstandardnew"] == pat]
        accs[col] = sub.groupby("user_id")["correct"].mean()
    acc_df = pd.DataFrame(accs).fillna(0.0)
    acc_df["combined_accuracy"] = acc_df.mean(axis=1)
    df = df.merge(acc_df, left_on="user_id", right_index=True, how="left")
    df["combined_accuracy"] = df["combined_accuracy"].fillna(0.0)

    df["user_question_count"] = df.groupby("user_id")["problem_id"].transform("nunique")

    # ----------------------------------------- order columns nicely
    front = [
        "id", "user_id", "problem_id", "topic_id",
        "created_at", "updated_at", "problem_appeared_at",
        "response_submitted_at", "duration", "answerChoiceIds",
        "title", "free", "passed", "score", "qscore",
        "contest_id", "mission_id",
        "Case ID", "Origin", "matchfile", "filename3",
        "Correct Label", "goldstandardnew",
        "experience_level", "preferred_specialty", "country", "locale",
        "group", "correct", "in_calibration", "qualified",
        "user_question_count",
        "GPDaccuracy", "LPDaccuracy", "grdaaccuracy", "lrdaaccuracy",
        "otheraccuracy", "seizureaccuracy", "combined_accuracy",
    ]
    front = [c for c in front if c in df.columns]
    rest = [c for c in df.columns if c not in front]
    df = df[front + rest]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nWrote {OUT} ({len(df):,} rows, {len(df.columns)} columns, "
          f"{OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
