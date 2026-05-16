"""Project-wide constants and paths."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "figures"

# Primary analysis dataframe: one row per (user, question) response, already
# merged with gold-standard labels, user metadata, and per-user/per-pattern
# calibration accuracies. Built by `scripts/build_test_df4.py` from the raw
# Centaur Labs exports and the prior Jing-2023 gold-standard MAT files; or
# obtain directly from the BDSP data folder.
TEST_DF4_PATH = DATA_DIR / "test_df4.csv"

# Centaur Labs user table (id, email, first, last, locale, experience_level).
# Used to map participant locale -> country for Supplemental S1.
USERS_PATH = DATA_DIR / "eeg-all-users-and-topics.csv"

# 30-expert gold-standard label matrix (one row per EEG segment, one column
# per expert; values 0-5 map to {other, seizure, lpd, gpd, lrda, grda}).
# Already published with Jing 2023 (Neurology); used for Supp S4/S5 only.
EXPERTS30_PATH = DATA_DIR / "labels_experts30.xlsx"

# Six SRPP (seizure / rhythmic-or-periodic-pattern) class labels.
SRPPS = ["gpd", "grda", "lpd", "lrda", "other", "seizure"]

# Numeric label mapping used in `labels_experts30.xlsx`.
LABEL_MAP = {0: "other", 1: "seizure", 2: "lpd", 3: "gpd", 4: "lrda", 5: "grda"}

# Non-inferiority margin (Section 2.4).
NONINF_MARGIN = 0.05

# Bonferroni-adjusted alpha for the 6 per-pattern non-inferiority tests
# (Section 2.4: "pattern-specific p-values were adjusted with Bonferroni
# correction ... with p < .025 considered statistically significant").
ALPHA_NI_PER_PATTERN = 0.025

# Crowd subgroups used in by-subgroup analyses (Section 2.8, Supp S10).
CROWD_SUBGROUPS = {
    "MD":            ["MD", "DO"],
    "MedStudent":    ["Medical Student"],
    "NP_PA_Pharm":   ["NP", "PA", "Pharmacist"],
    "OtherStudent":  ["NP Student", "PA Student", "Pharmacy Student",
                      "Other Healthcare Student"],
    "Other":         ["Other"],
}
