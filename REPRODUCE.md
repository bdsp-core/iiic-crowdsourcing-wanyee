# Reproduce — IIIC Crowdsourcing (Kong et al. 2025)

Regenerates **every figure, table, and supplemental analysis**. Verified 2026-07-06:
`reproduce_all.py` → **15/15 targets, 24 outputs**.

## One command
```bash
pip install -r requirements.txt
# get the 3 data files into data/ (see DATA_SOURCE.md; ~297 MB from S3)
python scripts/reproduce_all.py            # all targets
python scripts/reproduce_all.py --only figure2 figure3   # subset
python scripts/reproduce_all.py --skip figure5           # skip slow bootstrap
```
Outputs land in `figures/` (`.png` + `.pdf` + the underlying `.csv`).

## Targets → outputs
| Paper item | Script (`scripts/`) | Output(s) in `figures/` |
|---|---|---|
| Table 1 (participants) | `table1_participants.py` | `table1_*.csv` |
| Figure 2 (predicted accuracy) | `figure2_predicted_accuracy.py` | `figure2.{png,pdf,csv}` |
| Figure 3 (forest / non-inferiority) | `figure3_forest_plot.py` | `figure3.{png,pdf}`, `figure3_noninferiority.csv` |
| Figure 4 (individual experts) | `figure4_individual_experts.py` | `figure4.{png,pdf,csv}` |
| Figure 5 (bootstrap sample size) | `figure5_bootstrap_samplesize.py` | `figure5.{png,pdf}`, `figure5_bootstrap.csv` |
| Supp S1–S11 | `supp_s1_countries.py` … `supp_s11_accuracy_histograms.py` | `supp_s*.{png,pdf,csv}` |

`scripts/reproduce_all.py` (`ALL_TARGETS`) is the authoritative target→module map.

## Requirements
Python 3.9+; `requirements.txt` (numpy, pandas, scipy, statsmodels, matplotlib, seaborn, openpyxl, pycountry). Data source + provenance: `DATA_SOURCE.md`. Data files are **not** committed (they live on S3); only `data/raw/manifest.csv` is.
