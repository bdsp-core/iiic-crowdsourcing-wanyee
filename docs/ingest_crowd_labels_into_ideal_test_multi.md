# How to add the Kong et al. 2025 crowd labels to `ideal-test-multi`

Drop-in instructions for the maintainer of
[`ideal-test-multi/data/labels/`](https://github.com/.../ideal-test-multi) to
fold the 478,834 crowd annotations + 17,358 calibration annotations from
the Kong-et-al-2025 contest into the unified label tables.

The Kong 2025 contest scored ~8,900 EEG segments from the same MGH
patient pool that backs the `sparcnet50K` dataset in your unified tables.
Adding the crowd labels gives you ~496k new `(seg, rater, label_type,
value)` rows from a *non-expert* rater pool — exactly the labelset
you'd want for any study of crowd vs. expert performance.

---

## TL;DR

1. Download two files from BDSP S3:
   ```bash
   aws s3 cp s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/test_df4.csv  .
   ```
2. Drop [`scripts/ingest_iiic_crowdsourcing_labels.py`](../scripts/ingest_iiic_crowdsourcing_labels.py) (in this repo)
   into your `ideal-test-multi/scripts/`.
3. Run it. It will:
   - parse Wan-Yee's stems and cross-walk to your `sparcnet50K` `seg_id`s via
     `(old_file_recording, window_end_s)` with ±5 s tolerance,
   - **insert ~7,800 new contest segments** under a new `source_dataset =
     iiic_crowdsourcing:kong2025` into `segments.csv` (for stems that
     don't already map to a sparcnet50K seg_id),
   - **add 1,529 new crowd raters** (1,537 qualified users in Kong 2025,
     minus the 8 study experts who already exist as canonical raters in
     your `raters.csv`),
   - **append ~496k `(seg, rater, label_type=pattern_class, value, source_dataset)`
     rows** to `labels.csv` and refresh the per-segment IIIC vote tallies
     in `segment_labels.csv`,
   - **append one row** to `datasets.csv` documenting the new source.

Run time: ~2 minutes. No external dependencies beyond what `ideal-test-multi`
already uses (`pandas`).

---

## What's in the Kong 2025 dataset

Single per-response table at
`s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/test_df4.csv`
(283 MB, 496,217 rows × 43 cols). One row per (user, question).

Columns we actually use (the rest are Centaur Labs metadata):

| Column | Description |
|---|---|
| `user_id` (int) | Centaur Labs user ID — the crowd rater |
| `problem_id` (int) | Centaur Labs problem ID — the EEG segment scored |
| `title` (str) | The rater's pattern call (one of `gpd`, `grda`, `lpd`, `lrda`, `other`, `seizure`) |
| `goldstandardnew` (str) | The gold-standard label (mode of 30-expert votes if known, else Centaur's stored answer) |
| `experience_level` (str) | One of `Expert`, `MD`, `DO`, `Medical Student`, `NP`, `PA`, `Pharmacist`, `NP Student`, `PA Student`, `Pharmacy Student`, `Other Healthcare Student`, `Other` |
| `preferred_specialty` (str) | Self-reported specialty (`Neurology`, `Critical Care`, etc.) |
| `country` (str) | Self-reported country (ISO 2-letter, often null) |
| `in_calibration` (bool) | True for the user's calibration-set rows (each user has 6–12 of them), False for the test-set rows |
| `Origin` (str) | The `.png` image URL, contains the segment stem |
| `filename3` (str) | Segment stem alone (e.g. `abn10329_20120330_100857_1957`) |

Total: **1,537 qualified users × 8,904 unique segments**. The 8 study
experts (`experience_level == "Expert"`) are M. Brandon Westover, Jin
Jing, Aaron Struck, Fábio Nascimento, Andres Rodriguez, Masoom Desai,
Gregory Kapinos, Jong Woo Lee. The remaining 1,529 users are the
non-expert crowd.

---

## Schema mapping to your unified tables

### `labels.csv` rows

| your column | how to populate |
|---|---|
| `seg_id` | crosswalked sparcnet50K `seg_id` (when ±5 s match exists) **OR** a fresh `seg_id` you assign (for the ~12% of Kong segments not already in your `segments.csv`) |
| `rater_id` | for the 6 of 8 study experts already in your `raters.csv`: use the existing canonical `rater_id`; for the other 2 experts + 1,529 crowd raters: assign new `rater_id`s starting at `max(raters.rater_id) + 1` |
| `label_type` | `"pattern_class"` (same value sparcnet50K uses) |
| `value` | the `title` field, lowercase: one of `gpd`, `grda`, `lpd`, `lrda`, `other`, `seizure` (already matches your existing taxonomy) |
| `source_dataset` | `"iiic_crowdsourcing:kong2025"` (or `:expert` / `:crowd` to distinguish the 8 experts from the 1,529 crowd) |

### `raters.csv` rows (one per new rater)

| your column | how to populate |
|---|---|
| `rater_id` | next free integer |
| `canonical_name` | `"Kong2025 contest user <user_id>"` for crowd raters (no real names available — they're de-identified). For the 2 missing study experts use their real names: `"Masoom Desai"`, `"Gregory Kapinos"` |
| `aliases` | JSON list of one item: the Centaur Labs `user_id` as a string |
| `groups` | append `"iiic_crowdsourcing:kong2025"` (for crowd raters); for the experts also include `"iiic_crowdsourcing:kong2025"` in their existing groups list |
| `expertise_level` | `"expert"` for the 2 new study experts; for crowd, map `experience_level` -> `"experienced"` (MD/DO with neurology specialty), `"novice"` (medical/health students), or `"other"` (anything else) |
| `affiliation` | leave null |
| `years_eeg` | leave null |
| `neurologist` / `epileptologist` / `board_certified` | True for the 2 study experts; null for crowd |
| `n_segments_scored_roster` | count of unique `problem_id`s the user scored in Kong 2025 |
| `is_person` | `True` |

### `segments.csv` rows (only for Kong segments not already in sparcnet50K)

For the ~1,100 Kong stems that don't crosswalk to an existing sparcnet50K
`seg_id` (e.g. because sparcnet50K didn't sample that part of the
recording):

| your column | how to populate |
|---|---|
| `seg_id` | next free integer |
| `source_dataset` | `"iiic_crowdsourcing:kong2025"` |
| `file_key` | use the existing sparcnet50K `file_key` for the same recording if you have one; else null |
| `old_token` | patient prefix from the stem (e.g. `abn10329`) |
| `old_file_recording` | `<patient>_<date>_<time>` (e.g. `abn10329_20120330_100857`) |
| `subtype` | uppercase Kong `goldstandardnew` (`GPD`, `LPD`, ...) |
| `window_end_s` | the numeric offset at the end of the Kong stem |
| `window_center_s` | `window_end_s - 5` (Kong's 10 s contest window centred 5 s before the end) |
| `window_start_s` | `window_end_s - 10` |
| `s3_uri` | `https://centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/<SUBTYPE>/<stem>.png` if you want the contest image, or the same `morgoth1` path sparcnet50K uses if you want the source MAT |

### `segment_labels.csv`

Re-run your existing aggregation logic over the augmented `labels.csv` —
the per-segment vote tallies (`iiic_vote_*`) will now include both the
sparcnet50K expert votes AND the Kong 2025 crowd votes. If you want to
preserve the *expert-only* tallies (likely yes), keep them in their current
columns and add parallel `iiic_crowd_vote_*` columns.

### `datasets.csv`

Add one row:

```
iiic_crowdsourcing:kong2025  Kong et al. 2025 (Epilepsia) crowd-sourcing contest: 1,537 users (8 experts + 1,529 non-experts) scoring ~8,900 IIIC segments via the DiagnosUs app  s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/test_df4.csv  8904  1537  pattern_class  "Kong W-Y, Nascimento FA, Struck A, Duhaime E, Kapur S, Amorim E, Kapinos G, Rodriguez A, Thomas B, Desai M, Lee JW, Westover MB, Jing J. Evaluating crowdsourcing for ICU EEG annotation: A comparison with expert performance. Epilepsia. 2025;66(11):4366-4380. doi:10.1111/epi.18547"
```

---

## The 8 study experts → ideal-test-multi rater_id mapping

| Kong user_id | Name | ideal-test-multi rater_id | Status |
|---:|---|---:|---|
| 41816 | M. Brandon Westover | **97** | already canonical |
| 123180 | Jin Jing | **78** | already canonical (expertise_level = "experienced" — may want to promote) |
| 129198 | Fábio A. Nascimento | **55** | already canonical |
| 129995 | Andres Rodriguez | **10** | already canonical |
| 130226 | Aaron F. Struck | **0** | already canonical |
| 130262 | Jong Woo Lee | **80** | already canonical |
| 130067 | Masoom Desai | (new) | **add to raters.csv as expert** |
| 129968 | Gregory Kapinos | (new) | **add to raters.csv as expert** |

For the 1,529 crowd raters, assign new `rater_id`s sequentially starting
at `max(raters.rater_id) + 1`.

---

## Segment crosswalk: how the ±5 s match works

Wan-Yee's contest stems look like `<patient>_<YYYYMMDD>_<HHMMSS>_<offset>`
where `offset` is the end of a 10 s window measured in seconds from the
recording start (e.g. `abn10329_20120330_100857_1957` ⇒ the 10 s window
ending 1,957 s into the `abn10329_20120330_100857` recording).

Your `segments.csv` for sparcnet50K has the same recordings under
`old_file_recording`, with `window_start_s` / `window_center_s` /
`window_end_s` columns. We match Kong `offset` against the sparcnet50K
`window_end_s` (primary), `window_center_s` (fallback), or
`window_start_s` (last resort), within a ±5 s tolerance. This recovers
**7,778 of 8,904 stems (87.4%)** as matches into existing sparcnet50K
seg_ids; the remaining 1,126 need fresh `seg_id`s assigned (see
"`segments.csv` rows" above).

The match was verified end-to-end by reproducing **Supplemental S5** of
the paper (split-violin of study-experts-vs-gold-standard-experts pairwise
agreement) directly from the matched data.

---

## Recommended source_dataset naming

To keep crowd vs. expert distinguishable downstream:

```
iiic_crowdsourcing:kong2025:expert   # 8 study experts, 8,534 rows
iiic_crowdsourcing:kong2025:crowd    # 1,529 non-experts, 487,683 rows
```

This mirrors how you already split `sn1_combined_v2` into `:sn1`,
`:bonobo_only`, and `:fabio_spikeed`.

---

## Suggested rater grouping

For the 1,529 crowd raters, the `experience_level` column in `test_df4`
maps roughly onto your existing `expertise_level` taxonomy as:

| Kong `experience_level` | ideal-test-multi `expertise_level` | n |
|---|---|---:|
| `MD` + `Neurology` | `experienced` | (count from `preferred_specialty`) |
| `MD` (non-neurology) + `DO` | `experienced` | |
| `Medical Student`, `NP Student`, `PA Student`, `Pharmacy Student`, `Other Healthcare Student` | `novice` | majority |
| `NP`, `PA`, `Pharmacist` | `experienced` (low) | |
| `Other` | `other` | |

(Or just use `crowd` as a new expertise level if you prefer.)

---

## Ready-to-run ingestion script

In this repo: [`scripts/ingest_iiic_crowdsourcing_labels.py`](../scripts/ingest_iiic_crowdsourcing_labels.py).
Copy it into `ideal-test-multi/scripts/` and run from the `ideal-test-multi`
repo root:

```bash
python scripts/ingest_iiic_crowdsourcing_labels.py \
    --kong-test-df4 /path/to/test_df4.csv \
    --labels-dir   data/labels \
    --dry-run                # prints what it would do without writing

# Then for real:
python scripts/ingest_iiic_crowdsourcing_labels.py \
    --kong-test-df4 /path/to/test_df4.csv \
    --labels-dir   data/labels
```

The script writes a new version of each of `labels.csv`, `raters.csv`,
`segments.csv`, and `datasets.csv` to
`data/labels/_after_kong2025_ingest/` so you can diff before overwriting.

---

## Citation

Please cite the Kong 2025 paper if you use the crowd labels in any
analysis:

> Kong W-Y, Nascimento FA, Struck A, Duhaime E, Kapur S, Amorim E,
> Kapinos G, Rodriguez A, Thomas B, Desai M, Lee JW, Westover MB, Jing J.
> *Evaluating crowdsourcing for ICU EEG annotation: A comparison with
> expert performance.* **Epilepsia** 2025;66(11):4366-4380.
> [doi:10.1111/epi.18547](https://doi.org/10.1111/epi.18547)
