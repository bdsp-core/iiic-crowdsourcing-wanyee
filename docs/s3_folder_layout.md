# AWS S3 folder layout for the BDSP data release

This is the structure we'll upload into the BDSP-managed S3 bucket. The
top-level prefix will be the project's BDSP slug (substitute the real
bucket and prefix as appropriate; placeholders below).

```
s3://bdsp-opendata-credentialed/iiic-irr-crowd/
├── README.md
├── CHANGELOG.md
├── LICENSE.txt                          ← CC BY-NC 4.0
├── citation.bib
│
├── annotations/
│   ├── test_df4.csv                     ← canonical 45-column dataframe (PRIMARY)
│   ├── test_df4_dictionary.md           ← column-by-column data dictionary
│   ├── calibration_assignments.csv      ← which user-question pairs are calibration vs test
│   └── labels_experts30.xlsx            ← 30-expert pivoted label matrix (Jing 2023)
│
├── raw_contest_exports/                 ← Centaur Labs source exports
│   ├── 1251-all-reads_ac.csv            ← per-read responses (657k rows)
│   ├── 1251-all-users_deidentified.csv  ← user table, PII stripped
│   ├── eeg-all-users-and-topics_deidentified.csv
│   └── Results_SeizureLike_Patterns_Dec_12_2022.csv
│
├── eeg_signals/
│   ├── iiic_contest_eeg.h5              ← bundled 50s EEG + 4 spectrograms per segment (~12 GB)
│   └── iiic_contest_eeg_schema.md       ← schema doc with example reader snippets
│
├── contest_images/                      ← optional; only if Centaur lets us export the PNGs
│   ├── manifest.csv                     ← segment_id, srpp_label, png_filename, sha256
│   └── png/
│       └── {segment_id}.png             ← one PNG per question shown to participants
│
└── docs/
    ├── methods_summary.pdf              ← extracted from the published paper
    └── data_dictionary_full.pdf
```

## Notes on each top-level item

### `README.md`
Mirrors the GitHub repo README; points at https://github.com/bdsp-core/iiic-crowdsourcing-wanyee for code, lists each artifact in this folder, and explains the access policy.

### `LICENSE.txt`
Verbatim copy of `LICENSE` in the GitHub repo (CC BY-NC 4.0).

### `citation.bib`
BibTeX entry for the published paper:
```bibtex
@article{kong2025crowdsourcing,
  author  = {Kong, Wan-Yee and Nascimento, F{\'a}bio A. and Struck, Aaron and
             Duhaime, Erik and Kapur, Srishti and Amorim, Edilberto and
             Kapinos, Gregory and Rodriguez, Andres and Thomas, Brendan and
             Desai, Masoom and Lee, Jong Woo and Westover, M. Brandon and
             Jing, Jin},
  title   = {Evaluating crowdsourcing for ICU EEG annotation:
             A comparison with expert performance},
  journal = {Epilepsia},
  year    = {2025},
  volume  = {66},
  number  = {11},
  pages   = {4366--4380},
  doi     = {10.1111/epi.18547}
}
```

### `annotations/`
- **`test_df4.csv`** — primary input for the GitHub reproduction code. ~496k rows. Once `test_df4_dictionary.md` is written, this becomes the most-cited artifact in the dataset.
- **`labels_experts30.xlsx`** — only needed for Supp S4/S5; already published with Jing 2023.

### `raw_contest_exports/`
The exports straight from Centaur Labs, with PII columns (email, first, last, app_display_name) stripped from the user tables. `Results_SeizureLike_Patterns_Dec_12_2022.csv` is the per-question summary needed to rebuild `test_df4` from scratch (provenance).

### `eeg_signals/`
A single HDF5 archive instead of 10,000+ tiny .mat files. The schema and example reader code live in `iiic_contest_eeg_schema.md` and in the GitHub repo's `scripts/bundle_eeg_h5.py` doctring.

### `contest_images/`
Optional. If Centaur Labs is willing to release the contest PNGs we host them here so reviewers and follow-on researchers can see exactly what each participant saw. If not, users can regenerate them from `eeg_signals/iiic_contest_eeg.h5` using `scripts/contest_image_gen/make_contest_image.py` in the GitHub repo.

### `docs/`
Static PDFs for offline reading; the canonical sources are the markdown in the GitHub repo.

## De-identification done before upload

The following columns are stripped from any file headed to S3:

| File | Columns dropped |
|---|---|
| `eeg-all-users-and-topics.csv` | `email`, `first`, `last`, `app_display_name` |
| `1251-all-users.csv` | `email`, `first`, `last`, `app_display_name` |
| `1251-all-users_demo_info.csv` | (same as above; the rest, including `country` and `experience_level`, is kept) |
| `1251-all-reads_ac.csv` | none (already de-identified — only `user_id` and `problem_id`) |

The de-identification script will be `scripts/deidentify_for_release.py` and the user IDs are preserved as opaque integers so they still join consistently across files. Author identification is via the published-paper byline plus the metadata in `docs/authors.md`, **not** via these CSVs.

## Sizes (rough estimate)

| Path | Size |
|---|---|
| `annotations/test_df4.csv` | ~150 MB |
| `annotations/labels_experts30.xlsx` | ~1 MB |
| `raw_contest_exports/1251-all-reads_ac.csv` | 133 MB |
| `raw_contest_exports/*` (other CSVs) | ~3 MB combined |
| `eeg_signals/iiic_contest_eeg.h5` | **~12 GB** (dominant) |
| `contest_images/png/` (optional) | ~5 GB |
| Everything else | < 10 MB |
| **TOTAL** | **~12–18 GB** |
