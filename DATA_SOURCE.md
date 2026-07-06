# Data source & provenance — IIIC Crowdsourcing (Kong et al. 2025)

## Raw / source data (canonical home) — verified accessible 2026-07-06
- **bdsp.io project:** `87rztvzmyz9uh0esnd83` — *"Evaluating crowdsourcing for ICU EEG annotation"* → https://bdsp.io/content/87rztvzmyz9uh0esnd83/
- **DOI:** [10.60508/fn0v-8w16](https://doi.org/10.60508/fn0v-8w16)
- **S3:** `s3://bdsp-opendata-credentialed/iiic-irr-crowd/` — credentialed (BDSP DUA). **16 objects, ~10 GB** (confirmed present). File-level listing in `data/raw/manifest.csv`.

Contents: `annotations/` (`test_df4.csv` — the primary analysis dataframe; `labels_experts30.xlsx` — 30-expert gold standard from Jing 2023; `test_df4_dictionary.md`), `raw_contest_exports/` (de-identified Centaur Labs exports), `eeg_signals/iiic_contest_eeg.h5` (9.5 GB EEG signals + schema), `contest_images/`, README/LICENSE/citation.

## Get the data (needed to reproduce)
The figures/tables need only **3 files (~297 MB)**, not the 9.5 GB `.h5` (which is only for the image/release utilities). Apply for `iiic-irr-crowd` on bdsp.io, then download into `data/`:
```bash
# via the credentialed S3 (see data/raw/manifest.csv for the full listing)
aws s3 cp s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/test_df4.csv                         data/test_df4.csv
aws s3 cp s3://bdsp-opendata-credentialed/iiic-irr-crowd/annotations/labels_experts30.xlsx               data/labels_experts30.xlsx
aws s3 cp s3://bdsp-opendata-credentialed/iiic-irr-crowd/raw_contest_exports/eeg-all-users-and-topics_deidentified.csv  data/eeg-all-users-and-topics.csv
```
(`src/config.py` resolves these paths.) The data is **not** committed to this repo — only the manifest is.

## Raw → derived lineage
1. **Raw contest exports** (de-identified Centaur Labs reads/users) + the **Jing 2023 30-expert gold standard** → `scripts/build_test_df4.py` → `test_df4.csv` (one row per user×question, merged with gold labels + calibration accuracies).
2. **`scripts/reproduce_all.py`** turns `test_df4.csv` (+ users + experts30) into every figure/table via `scripts/<target>.py` — no EEG signals needed.

## Verification (2026-07-06)
`python scripts/reproduce_all.py` → **15/15 targets, 24 outputs** regenerated (Table 1, Figures 2–5, Supp S1–S11). Confirmed the data is accessible and every result reproduces.
