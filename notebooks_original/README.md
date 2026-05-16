# Original notebooks (preserved for reference)

These are the Jupyter notebooks Wan-Yee Kong originally used to analyse the data
and produce all figures and tables in the published paper. They have been
**scrubbed** to remove secrets and personally identifying information:

- a GitHub personal access token (now revoked) has been replaced with
  `<REDACTED_GH_TOKEN>` (mixed_modeling.ipynb).
- participant email addresses in printed dataframe outputs have been
  replaced with `<REDACTED_EMAIL>`.

The cleaned, modular reproduction of the same analyses lives in `../src/`
and `../scripts/`. **Use the scripts for reproducing the paper.** These
notebooks are kept here for historical/provenance reference only.

| Notebook | Original purpose |
|---|---|
| `build_test_df4.ipynb` | Upstream pipeline that builds `test_df4.csv` from raw Centaur Labs exports + IIIC `.mat` files (`csvforeachexpertlevelandcompletewithgoldstandard.ipynb` in the original Drive). |
| `IRR_gold_standard_and_expert.ipynb` | Inter-rater agreement analyses (Supp S4, S5). |
| `mixed_modeling.ipynb` | Mixed-effects modelling for Figs 2-3 and Table 1. |
| `crowd_vs_individual_expert.ipynb` | Figs 4-5 and most supplementals. |
