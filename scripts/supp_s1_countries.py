"""Supplemental S1: Participant's place of residence.

The paper version is built by merging test_df4 with eeg-all-users-and-topics
on user_id and tallying ``locale`` (which encodes the language and country,
e.g. ``en_PH``). If ``1251-all-users_demo_info.csv`` is available, we prefer
its explicit ``country`` column.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import pycountry  # type: ignore

from src.data_loading import load_test_df4, load_users


def code_to_name(code: str | float) -> str:
    if pd.isna(code):
        return "Unknown"
    try:
        c = pycountry.countries.get(alpha_2=code.upper())
        return c.name if c else code
    except Exception:
        return code


def main():
    df = load_test_df4()

    demo_path = ROOT / "data" / "1251-all-users_demo_info.csv"
    if demo_path.exists():
        demo = pd.read_csv(demo_path, usecols=["id", "country"])
        merged = df[["user_id"]].drop_duplicates().merge(
            demo, left_on="user_id", right_on="id", how="left"
        )
        out = (merged["country"].value_counts(dropna=False)
                 .rename_axis("code").reset_index(name="participants"))
    else:
        users = load_users()
        merged = df[["user_id"]].drop_duplicates().merge(
            users, left_on="user_id", right_on="id", how="left"
        )
        # 'locale' looks like 'en_PH'; the last 2 chars are the country.
        merged["country"] = merged["locale"].str.extract(r"_([A-Z]{2})", expand=False)
        out = (merged["country"].value_counts(dropna=False)
                 .rename_axis("code").reset_index(name="participants"))

    out["country_name"] = out["code"].apply(code_to_name)
    out = out[["country_name", "code", "participants"]].rename(
        columns={"country_name": "Country Name", "code": "Code", "participants": "Participants"}
    )

    print(out.to_string(index=False))
    out_path = ROOT / "figures" / "supp_s1_countries.csv"
    out.to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
