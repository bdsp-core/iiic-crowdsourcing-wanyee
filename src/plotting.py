"""Shared plotting helpers for the figure scripts."""
from __future__ import annotations

import matplotlib.pyplot as plt

# Paper palette (matches Wan-Yee's original figures as closely as plain rcParams allow).
COLORS = {
    "Expert_NW":  "#bcd4e6",  # light blue
    "Expert_WM":  "#3a6c89",  # dark navy
    "Crowd_NW":   "#84212c",  # dark red
    "Crowd_WM":   "#f0c987",  # mustard
    "Expert":     "#3a6c89",
    "Crowd":      "#84212c",
}

# Display names for the 6 SRPP classes + Overall.
LABEL_PRETTY = {
    "overall": "Overall",
    "seizure": "Seizure",
    "other":   "Other",
    "lrda":    "LRDA",
    "lpd":     "LPD",
    "grda":    "GRDA",
    "gpd":     "GPD",
}


def set_default_style():
    """Set a clean matplotlib style consistent across all figures."""
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
    })


def save_figure(fig, name: str, out_dir):
    """Save ``fig`` to both PNG and PDF in ``out_dir``."""
    from pathlib import Path
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.png", bbox_inches="tight")
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight")
