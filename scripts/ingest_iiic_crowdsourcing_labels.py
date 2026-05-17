"""Ingest the Kong 2025 crowd labels into the ideal-test-multi unified label tables.

Copy this script into ``ideal-test-multi/scripts/`` and run from that
repo's root. See ``docs/ingest_crowd_labels_into_ideal_test_multi.md``
in https://github.com/bdsp-core/iiic-crowdsourcing-wanyee for the full
walkthrough.

Usage::

    # Pull the source dataframe from BDSP first:
    aws s3 cp s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/test_df4.csv .

    python scripts/ingest_iiic_crowdsourcing_labels.py \\
        --kong-test-df4 test_df4.csv \\
        --labels-dir    data/labels \\
        --dry-run         # prints what it would do

    # Then for real:
    python scripts/ingest_iiic_crowdsourcing_labels.py \\
        --kong-test-df4 test_df4.csv \\
        --labels-dir    data/labels

Writes augmented copies of ``raters.csv``, ``segments.csv``, ``labels.csv``,
and ``datasets.csv`` to ``<labels-dir>/_after_kong2025_ingest/`` so they can
be diff'd before overwriting.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

CITATION = (
    "Kong W-Y, Nascimento FA, Struck A, Duhaime E, Kapur S, Amorim E, "
    "Kapinos G, Rodriguez A, Thomas B, Desai M, Lee JW, Westover MB, Jing J. "
    "Evaluating crowdsourcing for ICU EEG annotation: A comparison with expert "
    "performance. Epilepsia. 2025;66(11):4366-4380. doi:10.1111/epi.18547"
)

# Pre-mapped: the 8 Kong study experts -> ideal-test-multi rater_id (if it exists).
# rater_id = None means "create a new canonical rater row for this person".
STUDY_EXPERT_MAP = {
    41816:  {"name": "M. Brandon Westover",   "existing_rater_id": 97},
    123180: {"name": "Jin Jing",              "existing_rater_id": 78},
    129198: {"name": "Fabio A. Nascimento",   "existing_rater_id": 55},
    129995: {"name": "Andres Rodriguez",      "existing_rater_id": 10},
    130226: {"name": "Aaron F. Struck",       "existing_rater_id": 0},
    130262: {"name": "Jong Woo Lee",          "existing_rater_id": 80},
    130067: {"name": "Masoom Desai",          "existing_rater_id": None},
    129968: {"name": "Gregory Kapinos",       "existing_rater_id": None},
}

SOURCE_DATASET_BASE = "iiic_crowdsourcing:kong2025"
MATCH_TOLERANCE_S = 5


# ---------------------------------------------------------------------------
# Map Kong experience_level -> ideal-test-multi expertise_level bucket.
# ---------------------------------------------------------------------------
EXP_TO_EXPERTISE = {
    "Expert":                    "expert",
    "MD":                        "experienced",
    "DO":                        "experienced",
    "NP":                        "experienced",
    "PA":                        "experienced",
    "Pharmacist":                "experienced",
    "Medical Student":           "novice",
    "NP Student":                "novice",
    "PA Student":                "novice",
    "Pharmacy Student":          "novice",
    "Other Healthcare Student":  "novice",
    "Other":                     "other",
}


def parse_stem(stem: str):
    """Return (recording, offset) for a Kong contest stem, or (None, None)."""
    if not isinstance(stem, str):
        return None, None
    m = re.match(r"^([a-zA-Z]+\d+)_(\d{8})_(\d{6})_(\d+)$",
                 stem.replace(" copy", ""))
    if not m:
        return None, None
    return f"{m.group(1)}_{m.group(2)}_{m.group(3)}", int(m.group(4))


def build_segment_crosswalk(kong_df: pd.DataFrame,
                            segments: pd.DataFrame) -> dict:
    """Map each Kong stem -> (existing sparcnet50K seg_id) or None."""
    sp = segments[segments["source_dataset"] == "sparcnet50K"]
    sp_by_rec: dict[str, list] = {}
    for rec, sub in sp.groupby("old_file_recording"):
        sp_by_rec[rec] = sub[["seg_id", "window_start_s",
                              "window_center_s", "window_end_s"]].values

    out: dict[str, int | None] = {}
    for stem in kong_df["filename3"].dropna().unique():
        rec, off = parse_stem(stem)
        if rec is None:
            out[stem] = None; continue
        rows = sp_by_rec.get(rec)
        if rows is None:
            out[stem] = None; continue
        best = None; best_diff = MATCH_TOLERANCE_S + 1
        for sid, ws, wc, we in rows:
            for v in (we, wc, ws):
                d = abs(v - off)
                if d < best_diff:
                    best = int(sid); best_diff = d
        out[stem] = best
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kong-test-df4", required=True, type=Path,
                   help="Path to test_df4.csv from the Kong 2025 BDSP release")
    p.add_argument("--labels-dir", required=True, type=Path,
                   help="Path to ideal-test-multi/data/labels/")
    p.add_argument("--dry-run", action="store_true",
                   help="Print stats only; don't write any files")
    args = p.parse_args()

    print(f"Loading Kong test_df4 from {args.kong_test_df4} ...")
    kong = pd.read_csv(args.kong_test_df4, low_memory=False)
    # Make sure filename3 is set; the column from the build script is named
    # filename3 already, but some intermediate versions called it `stem`.
    if "filename3" not in kong.columns and "stem" in kong.columns:
        kong = kong.rename(columns={"stem": "filename3"})
    if "filename3" not in kong.columns:
        # derive from Origin / Origin_x
        url_col = next(c for c in ("Origin", "Origin_x", "matchfile") if c in kong.columns)
        kong["filename3"] = (kong[url_col].astype(str)
                             .str.extract(r"/([^/]+)\.png$", expand=False)
                             .str.replace(" copy", "", regex=False))
    print(f"  {len(kong):,} rows, {kong['user_id'].nunique():,} users, "
          f"{kong['filename3'].nunique():,} unique stems")

    print(f"Loading ideal-test-multi tables from {args.labels_dir} ...")
    raters   = pd.read_csv(args.labels_dir / "raters.csv")
    segments = pd.read_csv(args.labels_dir / "segments.csv", low_memory=False)
    labels   = pd.read_csv(args.labels_dir / "labels.csv", low_memory=False)
    datasets = pd.read_csv(args.labels_dir / "datasets.csv")
    print(f"  raters: {len(raters):,}  segments: {len(segments):,}  "
          f"labels: {len(labels):,}  datasets: {len(datasets):,}")

    # ----------------------------- segment crosswalk
    print(f"\nCross-walking Kong stems -> sparcnet50K seg_ids (±{MATCH_TOLERANCE_S}s) ...")
    stem_to_seg = build_segment_crosswalk(kong, segments)
    matched = sum(1 for v in stem_to_seg.values() if v is not None)
    unmatched_stems = [s for s, v in stem_to_seg.items() if v is None]
    print(f"  matched into existing sparcnet50K seg_ids: {matched:,}")
    print(f"  unmatched (will get new seg_ids):           {len(unmatched_stems):,}")

    next_seg_id = int(segments["seg_id"].max()) + 1
    new_segments_rows = []
    for stem in unmatched_stems:
        rec, off = parse_stem(stem)
        if rec is None:
            continue
        # Derive a subtype from Kong's gold standard for that stem (if any).
        gs = kong.loc[kong["filename3"] == stem, "goldstandardnew"].dropna()
        subtype = str(gs.iloc[0]).upper() if len(gs) else None
        new_segments_rows.append({
            "seg_id":              next_seg_id,
            "source_dataset":      SOURCE_DATASET_BASE,
            "old_token":           rec.split("_")[0],
            "old_file_recording":  rec,
            "subtype":             subtype,
            "window_start_s":      max(off - 10, 0),
            "window_center_s":     max(off - 5, 0),
            "window_end_s":        off,
            "s3_uri": (
                f"https://centaur-customer-uploads.s3.us-east-1.amazonaws.com/"
                f"mgh-eeg/{subtype or 'Other'}/{stem}.png"
            ),
            "s3_uri_note": "Kong 2025 contest PNG (10s EEG + 10min spec); "
                           "for the underlying .mat see the morgoth1 path "
                           "for the same old_file_recording.",
        })
        stem_to_seg[stem] = next_seg_id
        next_seg_id += 1
    new_segments = pd.DataFrame(new_segments_rows)
    print(f"  new segments rows: {len(new_segments):,}")

    # ----------------------------- rater table
    print("\nBuilding rater table ...")
    next_rater_id = int(raters["rater_id"].max()) + 1
    user_to_rater: dict[int, int] = {}
    new_raters_rows = []

    # 8 study experts.
    for uid, info in STUDY_EXPERT_MAP.items():
        if info["existing_rater_id"] is not None:
            user_to_rater[uid] = info["existing_rater_id"]
        else:
            user_to_rater[uid] = next_rater_id
            new_raters_rows.append({
                "rater_id":           next_rater_id,
                "canonical_name":     info["name"],
                "aliases":            json.dumps([f"kong2025:user_{uid}"]),
                "groups":             json.dumps([SOURCE_DATASET_BASE]),
                "expertise_level":    "expert",
                "neurologist":        True,
                "epileptologist":     True,
                "board_certified":    True,
                "is_person":          True,
            })
            next_rater_id += 1

    # 1,529 crowd raters (anonymous: name = Kong2025 contest user <user_id>).
    crowd_users = kong[~kong["user_id"].isin(STUDY_EXPERT_MAP)].copy()
    user_to_exp = (crowd_users.drop_duplicates("user_id")
                              .set_index("user_id")["experience_level"]
                              .to_dict())
    user_to_spec = (crowd_users.drop_duplicates("user_id")
                              .set_index("user_id")
                              .get("preferred_specialty", pd.Series(dtype=str))
                              .to_dict())
    user_to_n = crowd_users.groupby("user_id")["problem_id"].nunique().to_dict()
    for uid in sorted(user_to_exp):
        user_to_rater[int(uid)] = next_rater_id
        new_raters_rows.append({
            "rater_id":           next_rater_id,
            "canonical_name":     f"Kong2025 contest user {int(uid)}",
            "aliases":            json.dumps([f"kong2025:user_{int(uid)}"]),
            "groups":             json.dumps([SOURCE_DATASET_BASE]),
            "expertise_level":    EXP_TO_EXPERTISE.get(user_to_exp.get(uid), "other"),
            "affiliation":        user_to_spec.get(uid) or None,
            "n_segments_scored_roster": int(user_to_n.get(uid, 0)),
            "is_person":          True,
        })
        next_rater_id += 1
    new_raters = pd.DataFrame(new_raters_rows)
    print(f"  new rater rows: {len(new_raters):,} "
          f"({2 if any(STUDY_EXPERT_MAP[u]['existing_rater_id'] is None for u in STUDY_EXPERT_MAP) else 0} new experts + "
          f"{len(crowd_users['user_id'].unique()):,} crowd)")

    # ----------------------------- labels rows
    print("\nBuilding labels rows ...")
    new_labels = pd.DataFrame({
        "seg_id":         kong["filename3"].map(stem_to_seg).astype("Int64"),
        "rater_id":       kong["user_id"].map(user_to_rater).astype("Int64"),
        "label_type":     "pattern_class",
        "value":          kong["title"].str.lower(),
        "source_dataset": SOURCE_DATASET_BASE + ":" + (
            kong["user_id"].isin(STUDY_EXPERT_MAP).map({True: "expert", False: "crowd"})
        ),
    }).dropna(subset=["seg_id", "rater_id", "value"])
    print(f"  new labels rows: {len(new_labels):,}")
    print(f"    by source_dataset:")
    print(new_labels.groupby("source_dataset").size().to_string())

    # ----------------------------- datasets row
    new_dataset_row = {
        "dataset_id":           SOURCE_DATASET_BASE,
        "description":          ("Kong et al. 2025 (Epilepsia) crowdsourcing contest: "
                                 "1,537 users (8 experts + 1,529 non-experts) scoring "
                                 "~8,900 IIIC segments via the DiagnosUs app."),
        "source_path":          ("s3://bdsp-opendata-credentialed/iiic-irr-crowd/"
                                 "annotations/test_df4.csv"),
        "n_segments_in_source": int(kong["filename3"].nunique()),
        "n_raters_in_source":   int(kong["user_id"].nunique()),
        "label_types":          "pattern_class",
        "paper":                CITATION,
    }
    new_datasets = pd.DataFrame([new_dataset_row])

    # ----------------------------- write
    if args.dry_run:
        print("\n[--dry-run] Not writing any files.")
        return

    out_dir = args.labels_dir / "_after_kong2025_ingest"
    out_dir.mkdir(parents=True, exist_ok=True)

    pd.concat([raters, new_raters], ignore_index=True).to_csv(out_dir / "raters.csv", index=False)
    pd.concat([segments, new_segments], ignore_index=True).to_csv(out_dir / "segments.csv", index=False)
    pd.concat([labels, new_labels], ignore_index=True).to_csv(out_dir / "labels.csv", index=False)
    pd.concat([datasets, new_datasets], ignore_index=True).to_csv(out_dir / "datasets.csv", index=False)

    print(f"\nWrote augmented tables to {out_dir}/. Diff them against the "
          f"live versions before overwriting:\n")
    for name in ("raters", "segments", "labels", "datasets"):
        print(f"  diff <(head -1 {args.labels_dir}/{name}.csv) "
              f"<(head -1 {out_dir}/{name}.csv)  # column check")
        print(f"  cp {out_dir}/{name}.csv {args.labels_dir}/{name}.csv  # promote")


if __name__ == "__main__":
    main()
