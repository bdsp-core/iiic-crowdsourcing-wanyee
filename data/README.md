# `data/` — input files for the analyses

This directory is **intentionally empty in version control**. All input files
are too large or contain identifiable information that can't be checked into
the public GitHub repository. Instead, download them from the BDSP project:

> **BDSP page:** https://bdsp.io/projects/87rztvzmyz9uh0esnd83/

After downloading, place the files here so the scripts in `../scripts/` can
find them. The expected paths are configured in [`../src/config.py`](../src/config.py).

## Files expected by the analysis code

| File | Required by | Notes |
|---|---|---|
| `test_df4.csv` | **all main figures + supplementals except S3, S5** | Master per-response dataframe (~478k rows). One row per (user_id, problem_id) response with gold-standard label and per-user calibration weights already merged. See `../docs/data_dictionary.md`. |
| `eeg-all-users-and-topics.csv` | Supp S1 (fallback) | Centaur Labs user table. PII columns (email, first, last) are dropped by `src.data_loading.load_users`. |
| `1251-all-users_demo_info.csv` | Supp S1 (preferred) | Per-user demographics with explicit `country`. Used preferentially over the locale field when available. |
| `labels_experts30.xlsx` | Supp S4, S5 | 30-expert pivoted label matrix from the Jing et al. 2023 *Neurology* paper. Numeric labels 0-5 map to {other, seizure, lpd, gpd, lrda, grda}. |

## Provenance (upstream pipeline)

The `test_df4.csv` file is itself derived from raw Centaur Labs exports plus
the prior IIIC gold-standard labeling effort (Jing et al., 2023). The
upstream pipeline, originally implemented in
`notebooks_original/csvforeachexpertlevelandcompletewithgoldstandard.ipynb`,
proceeds as follows:

1. Load Centaur Labs per-question summary
   (`Results SeizureLike Patterns Dec 12 2022 18.50.01 PM.csv`) — has
   `Case ID`, `Origin`, `Correct Label`.
2. Load Centaur Labs per-read individual responses
   (`1251-all-reads_ac.csv`).
3. Merge on `Case ID == problem_id` to attach the `Origin` (S3 image URL)
   to every read.
4. From the Jing-2023 IIIC `.mat` files (one MAT per segment), read the
   `votes` array (six counts) and take its argmax (`max_column`) as the
   30-expert gold-standard label whenever the segment received ≥10 votes.
5. Define `goldstandardnew = max_column if not null else Correct Label`.
6. Merge in the Centaur Labs user table for `experience_level` and
   `preferred_specialty`.
7. Compute per-user, per-pattern calibration accuracies (the six
   `*accuracy` columns) on the calibration subset.
8. Output `test_df4.csv`.

## EEG images

The `matchfile` column of `test_df4.csv` records the URL of the contest PNG
shown to each rater. Format:

    https://centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/{LABEL}/{stub}.png

Each PNG is a 10-second EEG epoch in bipolar montage, accompanied by a 10-minute
spectrogram (Figure 1 of the paper). If a download of the PNGs is needed for
your reproduction, the BDSP folder mirrors them under `images/`.
