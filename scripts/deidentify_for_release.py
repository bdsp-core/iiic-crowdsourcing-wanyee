"""Deidentify the Centaur user-table exports and stage everything for S3 upload.

Run from the repo root. Produces:

    staging/
      LICENSE.txt
      README.md
      citation.bib
      CHANGELOG.md
      raw_contest_exports/
        1251-all-reads_ac.csv                                   (copy)
        1251-all-users_deidentified.csv                         (drop PII cols)
        1251-all-users_demo_info_deidentified.csv               (drop PII cols)
        eeg-all-users-and-topics_deidentified.csv               (drop PII cols)
        Results_SeizureLike_Patterns_Dec_12_2022.csv            (rename of centaur_summary.csv)

The annotations/ and eeg_signals/ subdirs are added separately once
test_df4.csv, labels_experts30.xlsx, and the bundled .h5 are ready.
"""

import os
import shutil
import sys

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
STAGING = os.path.join(REPO, "staging")
RAW = os.path.join(STAGING, "raw_contest_exports")

PII_COLUMNS = {"email", "first", "last", "app_display_name"}


def deidentify(src_basename, dst_basename):
    src = os.path.join(DATA, src_basename)
    dst = os.path.join(RAW, dst_basename)
    df = pd.read_csv(src)
    dropped = [c for c in df.columns if c in PII_COLUMNS]
    df = df.drop(columns=dropped)
    df.to_csv(dst, index=False)
    print(f"  {src_basename:40s} -> {dst_basename:50s}  rows={len(df):6d}  dropped={dropped}")


def copy(src_basename, dst_basename):
    src = os.path.join(DATA, src_basename)
    dst = os.path.join(RAW, dst_basename)
    shutil.copyfile(src, dst)
    print(f"  {src_basename:40s} -> {dst_basename:50s}  bytes={os.path.getsize(dst):,d}")


def write_text(rel_path, content):
    dst = os.path.join(STAGING, rel_path)
    with open(dst, "w") as f:
        f.write(content)
    print(f"  wrote staging/{rel_path:40s}  bytes={os.path.getsize(dst):,d}")


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(STAGING, exist_ok=True)

    print("=== De-identified user-table CSVs ===")
    deidentify("eeg-all-users-and-topics.csv", "eeg-all-users-and-topics_deidentified.csv")
    deidentify("1251-all-users.csv",           "1251-all-users_deidentified.csv")
    deidentify("1251-all-users_demo_info.csv", "1251-all-users_demo_info_deidentified.csv")

    print("\n=== Already-de-identified file (copied as-is) ===")
    copy("1251-all-reads_ac.csv", "1251-all-reads_ac.csv")
    copy("centaur_summary.csv",   "Results_SeizureLike_Patterns_Dec_12_2022.csv")

    print("\n=== Static files ===")
    shutil.copyfile(os.path.join(REPO, "LICENSE"),   os.path.join(STAGING, "LICENSE.txt"))
    shutil.copyfile(os.path.join(REPO, "README.md"), os.path.join(STAGING, "README.md"))
    print(f"  copied LICENSE -> staging/LICENSE.txt")
    print(f"  copied README.md -> staging/README.md")

    write_text("citation.bib", """\
@article{kong2025crowdsourcing,
  author  = {Kong, Wan-Yee and Nascimento, F{\\'a}bio A. and Struck, Aaron and
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
""")

    write_text("CHANGELOG.md", """\
# Changelog

## 1.0.0 -- 2026-05-16 (initial release)
- Initial public release accompanying the published manuscript
  (Epilepsia, 2025; doi:10.1111/epi.18547).
- Raw contest exports (de-identified) and static documents.
- Annotations (test_df4.csv, labels_experts30.xlsx) and the bundled
  EEG-signal HDF5 will be uploaded in a subsequent revision once
  upstream sources are available.
""")

    print("\n=== Staging tree summary ===")
    for root, dirs, files in os.walk(STAGING):
        rel = os.path.relpath(root, STAGING) or "."
        for f in sorted(files):
            full = os.path.join(root, f)
            print(f"  {rel + '/' + f:55s}  {os.path.getsize(full):>13,d} bytes")


if __name__ == "__main__":
    main()
