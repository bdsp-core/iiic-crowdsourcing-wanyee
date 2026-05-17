"""Reconstruct ``labels_experts30.xlsx`` from the ideal-test-multi unified label tables.

The source is the canonical IIIC label repository in
``/Users/mwestover/GithubRepos/ideal-test-multi/data/labels/`` (built by
that repo's ``scripts/build_unified_labels.py``), specifically the
``sparcnet50K`` slice (50,478 segments × 124 raters, one row per
(seg, rater, label_type)).

We cross-walk each of Wan-Yee's contest stems (parsed from the slim
``goldstandardnew925.csv``) to the corresponding sparcnet50K ``seg_id``
by matching ``(old_file_recording, window_end_s)`` with ±5 s tolerance;
then pivot the long-form ``labels.csv`` into the wide-form expected by
``Copy_of_IRR_gold_standard_and_expert.ipynb``:

    file_name  goldstandardnew  E001  E002  ... E030
    abn10329_20120330_100857_1957  other  0  ...  3
    ...

with values in {0..5} per Wan-Yee's mapping
{0=other, 1=seizure, 2=lpd, 3=gpd, 4=lrda, 5=grda}.

The 30 columns are the 30 most-active expert raters in sparcnet50K (which
matches the 30 named expert raters in Jing et al., 2023 *Neurology*).
Rater names themselves are NOT included; columns are anonymous E001..E030.

Output: staging/annotations/labels_experts30.xlsx
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

IDEAL = Path("/Users/mwestover/GithubRepos/ideal-test-multi/data/labels")
SLIM = ROOT / "data" / "goldstandardnew925.csv"
OUT = ROOT / "staging" / "annotations" / "labels_experts30.xlsx"

LABEL_TO_INT = {"other": 0, "seizure": 1, "lpd": 2, "gpd": 3, "lrda": 4, "grda": 5}
MATCH_TOLERANCE_S = 5

import re


def main():
    # ----------------------------- Wan-Yee contest stems
    print("Parsing Wan-Yee contest stems …")
    df = pd.read_csv(SLIM, usecols=["Origin_x", "goldstandardnew"])
    df["stem"] = (df["Origin_x"].astype(str)
                  .str.extract(r"/([^/]+)\.png$", expand=False)
                  .str.replace(" copy", "", regex=False))
    df = df.dropna(subset=["stem"]).drop_duplicates("stem")
    wanyee = []
    for _, r in df.iterrows():
        m = re.match(r"^([a-zA-Z]+\d+)_(\d{8})_(\d{6})_(\d+)$", r["stem"])
        if m:
            wanyee.append({
                "file_name": r["stem"],
                "old_file_recording": f"{m.group(1)}_{m.group(2)}_{m.group(3)}",
                "offset": int(m.group(4)),
                "goldstandardnew_wy": str(r["goldstandardnew"]).lower(),
            })
    wanyee = pd.DataFrame(wanyee)
    print(f"  {len(wanyee):,} unique contest stems")

    # ----------------------------- sparcnet50K segments + labels
    print("Loading sparcnet50K segment table …")
    segs = pd.read_csv(IDEAL / "segments.csv", low_memory=False)
    sp = segs[segs["source_dataset"] == "sparcnet50K"][
        ["seg_id", "old_file_recording", "window_start_s",
         "window_center_s", "window_end_s"]
    ].copy()
    print(f"  {len(sp):,} sparcnet50K segments")

    print("Loading sparcnet50K labels …")
    labels = pd.read_csv(IDEAL / "labels.csv", low_memory=False)
    sp_labels = labels[(labels["source_dataset"] == "sparcnet50K") &
                       (labels["label_type"] == "pattern_class")][
        ["seg_id", "rater_id", "value"]
    ].copy()
    sp_labels["value"] = sp_labels["value"].str.lower()
    print(f"  {len(sp_labels):,} (seg × rater) pattern-class labels")

    # ----------------------------- pick the top-30 raters by activity
    print("Selecting top-30 raters by # segments scored …")
    rater_counts = sp_labels.groupby("rater_id")["seg_id"].nunique()\
                            .sort_values(ascending=False)
    raters = pd.read_csv(IDEAL / "raters.csv").set_index("rater_id")
    # Keep only expert-level raters (per the README's expertise_level field)
    expert_only = rater_counts.index.intersection(
        raters[raters["expertise_level"] == "expert"].index
    )
    rater_counts = rater_counts.loc[expert_only]
    top30 = rater_counts.head(30).index.tolist()
    print(f"  Top 30 expert raters' names:")
    for i, rid in enumerate(top30, start=1):
        print(f"    E{i:03d}  (rater_id={rid:>4})  "
              f"{raters.loc[rid, 'canonical_name']}  ({int(rater_counts[rid]):,} segs)")
    rater_to_col = {rid: f"E{i:03d}" for i, rid in enumerate(top30, start=1)}

    # ----------------------------- fuzzy match Wan-Yee stems -> seg_id
    print(f"\nMatching stems to sparcnet seg_ids (±{MATCH_TOLERANCE_S}s tolerance)…")
    sp_by_rec = {rec: sub.to_dict("records")
                 for rec, sub in sp.groupby("old_file_recording")}
    matched = []
    for _, r in wanyee.iterrows():
        rows = sp_by_rec.get(r["old_file_recording"], [])
        best = None
        best_diff = MATCH_TOLERANCE_S + 1
        for s in rows:
            for col in ("window_end_s", "window_center_s", "window_start_s"):
                d = abs(s[col] - r["offset"])
                if d < best_diff:
                    best = s["seg_id"]; best_diff = d
        if best is not None:
            matched.append({"file_name": r["file_name"],
                            "seg_id": int(best),
                            "goldstandardnew": r["goldstandardnew_wy"]})
    matched = pd.DataFrame(matched)
    print(f"  Matched: {len(matched):,} of {len(wanyee):,} stems "
          f"({100*len(matched)/len(wanyee):.1f}%)")

    # ----------------------------- pivot labels → wide
    print("Pivoting labels into wide format …")
    sub = sp_labels[(sp_labels["seg_id"].isin(matched["seg_id"])) &
                    (sp_labels["rater_id"].isin(top30))].copy()
    wide = sub.pivot_table(index="seg_id", columns="rater_id",
                           values="value", aggfunc="first")
    # Rename columns -> E001..E030 and map text -> int
    wide = wide.rename(columns=rater_to_col)
    wide = wide.reindex(columns=[f"E{i:03d}" for i in range(1, 31)])
    for col in wide.columns:
        wide[col] = wide[col].map(LABEL_TO_INT)

    # Attach file_name (Wan-Yee stem) + goldstandardnew via the match table
    out = matched.merge(wide, left_on="seg_id", right_index=True, how="left")
    out = out.drop(columns=["seg_id"])
    out = out[["file_name", "goldstandardnew"] + [f"E{i:03d}" for i in range(1, 31)]]
    # Drop rows where every expert column is NaN (no labels for that segment).
    expert_cols = [c for c in out.columns if c.startswith("E")]
    out = out[out[expert_cols].notna().any(axis=1)].copy()
    print(f"\nFinal table: {len(out):,} rows × {len(out.columns)} cols")
    print(f"  Per-segment expert coverage: "
          f"min={out[expert_cols].notna().sum(axis=1).min()}, "
          f"max={out[expert_cols].notna().sum(axis=1).max()}, "
          f"mean={out[expert_cols].notna().sum(axis=1).mean():.1f}")

    # ----------------------------- save
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_excel(OUT, index=False)
    print(f"\nWrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
