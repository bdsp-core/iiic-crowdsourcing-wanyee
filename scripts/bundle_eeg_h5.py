"""Bundle Jin Jing's per-segment .mat EEG files into a single HDF5 archive.

Each .mat file contains:
  * data_50sec : (21, 10000) float64 -- 50 s of EEG at 200 Hz across 21 channels
  * spec_10min : (4, 2) cell array -- 4 spectrograms (LL/RL/LP/RP) of shape
                 (100, 300), with the row label string in column 0 and the
                 spectrogram array in column 1

In the published HDF5 file we store the data downcast to float32 (max abs
error < 1e-4 μV vs the float64 source, an order of magnitude below clinical
EEG noise) with gzip-9 compression and chunking sized for typical access
patterns. Each segment becomes a group ``/segments/<segment_id>/`` holding
``data_50sec`` plus four ``spec_<region>`` datasets. The 30-expert gold
standard labels are merged in too, when supplied.

Usage
-----
$ python scripts/bundle_eeg_h5.py --mat-dir /path/to/Data \\
    --out data/iiic_contest_eeg.h5 \\
    --annotations data/test_df4.csv \\
    --experts30 data/labels_experts30.xlsx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scipy.io as sio
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import LABEL_MAP, SRPPS

SAMPLING_RATE_HZ = 200
EEG_CHANNELS_21 = [
    "Fp1", "F3", "C3", "P3", "F7", "T3", "T5", "O1",
    "Fz", "Cz", "Pz",
    "Fp2", "F4", "C4", "P4", "F8", "T4", "T6", "O2",
    "EKG", "Photic",   # the last two depend on collection — adjust if needed
]


def open_mat(path: Path) -> dict:
    """Read one .mat file and return its data_50sec + four spectrograms."""
    d = sio.loadmat(str(path))
    data = d["data_50sec"]                     # (21, 10000) float64
    spec_cell = d["spec_10min"]                # (4, 2) object
    specs = {}
    for row in spec_cell:
        # row[0] is the region-name array (e.g., ['LL']); row[1] is the spec array.
        region = str(row[0][0])
        specs[region] = row[1]
    return {"data_50sec": data, "specs": specs}


def stem_to_segment_id(path: Path) -> str:
    """File stem -> segment id used as the HDF5 group key."""
    return path.stem


def collect_annotations(annotations_csv: Path) -> pd.DataFrame:
    """Pull per-segment metadata out of test_df4.csv (or the slim equivalent).

    We keep one row per problem_id with the gold-standard label, the
    Centaur image URL, the patient_id and timestamp parsed from the stem.
    """
    df = pd.read_csv(annotations_csv, low_memory=False)
    # ``Origin_x`` or ``Origin`` holds the S3 URL (or relative path);
    # ``matchfile`` holds the same on the wider test_df4.
    url_col = next((c for c in ["matchfile", "Origin_x", "Origin"]
                    if c in df.columns), None)
    if url_col is None:
        raise ValueError(f"No URL column found in {annotations_csv}")

    keep = df[["problem_id", url_col, "goldstandardnew"]].drop_duplicates("problem_id").copy()
    keep = keep.rename(columns={url_col: "contest_image_url"})
    # The Centaur URL ends with /{stem}.png -- extract the stem to match .mat files.
    keep["segment_id"] = (
        keep["contest_image_url"].astype(str)
        .str.extract(r"/([^/]+)\.png$", expand=False)
    )
    keep = keep.dropna(subset=["segment_id"])
    # Patient id and timestamp parts are the leading components of the stem,
    # e.g. ``pat1273_20111026_174800_3128`` -> patient_id=pat1273.
    keep["patient_id"] = keep["segment_id"].str.split("_").str[0]
    return keep.set_index("segment_id")


def load_experts30(path: Path) -> pd.DataFrame:
    """Load labels_experts30.xlsx and remap numeric labels 0-5 -> SRPP strings."""
    dfg = pd.read_excel(path)
    exclude = {"file_name", "goldstandardnew", "found_labels"}
    expert_cols = [c for c in dfg.columns if c not in exclude]
    for c in expert_cols:
        dfg[c] = dfg[c].map(LABEL_MAP)
    return dfg.set_index("file_name")


def write_segment(h5_root: h5py.Group, segment_id: str, mat: dict,
                  ann_row: pd.Series | None,
                  experts30_row: pd.Series | None):
    """Write a single /segments/<segment_id>/ group."""
    if segment_id in h5_root:
        del h5_root[segment_id]  # idempotent overwrite when re-running
    grp = h5_root.create_group(segment_id)

    # data_50sec: chunk per channel so single-channel slicing is fast.
    data = mat["data_50sec"].astype(np.float32)
    grp.create_dataset("data_50sec", data=data,
                       chunks=(1, data.shape[1]),
                       compression="gzip", compression_opts=9)

    for region, arr in mat["specs"].items():
        arr32 = arr.astype(np.float32)
        grp.create_dataset(f"spec_{region}", data=arr32,
                           chunks=arr32.shape,
                           compression="gzip", compression_opts=9)

    if ann_row is not None:
        grp.attrs["gold_standard_label"] = str(ann_row.get("goldstandardnew", ""))
        grp.attrs["contest_image_url"] = str(ann_row.get("contest_image_url", ""))
        grp.attrs["patient_id"] = str(ann_row.get("patient_id", ""))

    if experts30_row is not None:
        votes = {p: 0 for p in SRPPS}
        for v in experts30_row.values:
            if isinstance(v, str) and v in votes:
                votes[v] += 1
        for k, v in votes.items():
            grp.attrs[f"gold_votes_{k}"] = int(v)


def write_index(h5: h5py.File, segment_ids: list[str], expert_cols: list[str] | None):
    if "index" in h5:
        del h5["index"]
    idx = h5.create_group("index")
    idx.create_dataset("segment_ids", data=np.asarray(segment_ids, dtype="S"))
    if expert_cols:
        idx.create_dataset("expert_ids",
                           data=np.asarray(expert_cols, dtype="S"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mat-dir", type=Path, required=True,
                        help="Directory containing the per-segment .mat files (searched recursively)")
    parser.add_argument("--out", type=Path, required=True,
                        help="Output HDF5 path")
    parser.add_argument("--annotations", type=Path, default=None,
                        help="test_df4.csv (or goldstandardnew925.csv) for per-segment metadata")
    parser.add_argument("--experts30", type=Path, default=None,
                        help="labels_experts30.xlsx for 30-expert vote tallies")
    parser.add_argument("--limit", type=int, default=None,
                        help="Stop after N segments (sanity-check runs)")
    args = parser.parse_args()

    mat_files = sorted(args.mat_dir.rglob("*.mat"))
    if args.limit is not None:
        mat_files = mat_files[: args.limit]
    if not mat_files:
        raise SystemExit(f"No .mat files found under {args.mat_dir}")
    print(f"Found {len(mat_files)} .mat files under {args.mat_dir}")

    annotations = collect_annotations(args.annotations) if args.annotations else pd.DataFrame()
    experts30 = load_experts30(args.experts30) if args.experts30 else pd.DataFrame()
    expert_cols = experts30.columns.tolist() if not experts30.empty else None

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(args.out, "w") as h5:
        # Root attributes.
        h5.attrs["sampling_rate_hz"] = SAMPLING_RATE_HZ
        h5.attrs["srpp_labels"] = np.asarray(SRPPS, dtype="S")
        h5.attrs["channel_names_21"] = np.asarray(EEG_CHANNELS_21, dtype="S")
        h5.attrs["description"] = (
            "Per-segment 50 s EEG (21 channels @ 200 Hz) + four 10 min "
            "spectrograms, bundled from Jin Jing's MATLAB exports for the "
            "DiagnosUs IIIC crowdsourcing contest. See "
            "https://github.com/bdsp-core/iiic-crowdsourcing-wanyee."
        )
        segs = h5.create_group("segments")
        segment_ids = []
        for f in tqdm(mat_files, desc="Bundling"):
            sid = stem_to_segment_id(f)
            try:
                mat = open_mat(f)
            except Exception as e:
                print(f"  [skip] {f.name}: {type(e).__name__}: {e}")
                continue
            ann = annotations.loc[sid] if sid in annotations.index else None
            ex30 = experts30.loc[sid] if (not experts30.empty
                                          and sid in experts30.index) else None
            write_segment(segs, sid, mat, ann, ex30)
            segment_ids.append(sid)

        write_index(h5, segment_ids, expert_cols)
        print(f"Wrote {len(segment_ids)} segments to {args.out}")
        # Report final size.
        sz_mb = args.out.stat().st_size / (1024 ** 2)
        print(f"Output size: {sz_mb:.1f} MB")


if __name__ == "__main__":
    main()
