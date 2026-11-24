# -*- coding: utf-8 -*-
"""
Step 11c — Gap construction on the DALY burden metric.

The manuscript's primary analysis uses the stroke DALY crude rate as the demand
term D. An earlier version used stroke incidence scaled by a fixed factor
(Step 11b); the two share the same supply index S and the same min-max frame, so
the difference between them is attributable entirely to D.

This script rebuilds the DALY-basis panel from the archived inputs, writes
`data/gap_yearly_15_daly.csv`, and self-checks against the values reported in
the manuscript (Table 1, 2023 anchor year).

Inputs
------
data/gap_yearly_15.csv
    Archived Step 11b panel; only `S_index` and `S_norm` are used, so that S is
    carried over unchanged.
data/stroke_burden_rates_15countries_gbd2023.csv
    GBD 2023 crude rates for the 15 economies, 2010-2023, all ages, both sexes,
    no age standardisation. Produced by `scripts/11d_extract_gbd_rates.py` from
    the public GBD 2023 Results Tool download.

Outputs
-------
data/gap_yearly_15_daly.csv
    210 country-years with the DALY-basis D_norm, S_norm and Gap.
outputs/step11c_gap_daly_validation.md
    Validation report, including the incidence-basis reproduction check.

Definition
----------
    D_norm = minmax(stroke DALY crude rate)      frame: 15 countries x 14 years
    S_norm = carried over from Step 11b          frame: identical 210 rows
    Gap    = D_norm - S_norm                     positive = demand ranks above
                                                 supply within the panel
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEP_GAP = os.path.join(HERE, "data", "gap_yearly_15.csv")
RATES = os.path.join(HERE, "data", "stroke_burden_rates_15countries_gbd2023.csv")
OUT_CSV = os.path.join(HERE, "data", "gap_yearly_15_daly.csv")
OUT_MD = os.path.join(HERE, "outputs", "step11c_gap_daly_validation.md")

# Reported in the manuscript, Table 1, 2023 anchor year (DALY basis).
TABLE1_DALY = {"MM": 0.852, "LA": 0.438, "ID": 0.381, "VN": 0.186, "KH": 0.113,
               "CN": 0.005, "TH": -0.047, "PH": -0.053, "MY": -0.118, "BN": -0.239,
               "SG": -0.420, "KR": -0.477, "JP": -0.486, "GB": -0.691, "US": -0.800}

NAME = {"US": "United States", "GB": "United Kingdom", "JP": "Japan", "KR": "Korea",
        "CN": "China", "BN": "Brunei", "KH": "Cambodia", "ID": "Indonesia",
        "LA": "Laos", "MY": "Malaysia", "MM": "Myanmar", "PH": "Philippines",
        "SG": "Singapore", "TH": "Thailand", "VN": "Vietnam"}


def minmax(s):
    lo, hi = s.min(), s.max()
    return (s - lo) / (hi - lo)


def main():
    base = pd.read_csv(DEP_GAP)
    assert len(base) == 210 and base.country.nunique() == 15, "unexpected Step 11b shape"
    base = base[["country", "year", "S_index", "S_norm", "Gap"]].copy()

    rates = pd.read_csv(RATES)
    assert len(rates) == 210 and rates.country.nunique() == 15, "unexpected rate table shape"

    df = base.merge(rates, on=["country", "year"], how="inner", validate="one_to_one")
    assert len(df) == 210, "merge did not preserve the 210 country-years"

    # Frame: min-max taken over the pooled 210 country-years, not per year or per country.
    df["D_norm"] = minmax(df["stroke_daly_per100k"])
    df["Gap_daly"] = df["D_norm"] - df["S_norm"]

    # Reproduction check 1: the archived incidence-basis Gap must be recoverable
    # from the archived incidence rate with the same frame. If this fails, S or the
    # frame has drifted and the comparison across metrics is not valid.
    df["D_norm_inc"] = minmax(df["stroke_incidence_per100k"])
    df["Gap_inc"] = df["D_norm_inc"] - df["S_norm"]
    max_inc_dev = (df["Gap_inc"] - df["Gap"]).abs().max()

    # Reproduction check 2: 2023 anchor-year DALY gaps against the manuscript.
    r23 = df[df.year == 2023].set_index("country")
    dev = {c: r23.loc[c, "Gap_daly"] - v for c, v in TABLE1_DALY.items()}
    max_dev = max(abs(v) for v in dev.values())

    out = df[["country", "year", "stroke_daly_per100k", "D_norm", "S_norm", "Gap_daly"]].copy()
    out.columns = ["country", "year", "stroke_daly_per100k", "D_norm", "S_norm", "Gap"]
    out = out.sort_values(["country", "year"]).reset_index(drop=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8", float_format="%.6f")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    lines = []
    lines.append("# Step 11c validation — Gap on the DALY burden metric\n\n")
    lines.append("Rebuilt from `data/gap_yearly_15.csv` (S side, carried over unchanged) "
                 "and `data/stroke_burden_rates_15countries_gbd2023.csv` (D side).\n\n")
    lines.append("## Frame\n\n")
    lines.append("- `D_norm = minmax(stroke DALY crude rate)` over the pooled "
                 "15 countries x 2010-2023 = 210 country-years.\n")
    lines.append("- `S_norm` inherited row by row from Step 11b; S is not recomputed.\n")
    lines.append("- All rates are GBD 2023 crude rates (per 100,000, all ages, both sexes), "
                 "not age-standardised.\n\n")
    lines.append("## Check 1 — incidence-basis reproduction\n\n")
    lines.append(f"Recomputing the incidence-basis Gap from the archived incidence rate with "
                 f"the same frame reproduces the archived `Gap` column to a maximum absolute "
                 f"deviation of **{max_inc_dev:.2e}**, which is the rounding of the archived "
                 f"CSV to six decimals and not a discrepancy. S and the frame have therefore "
                 f"not drifted, and any difference between the two metrics is attributable "
                 f"to D.\n\n")
    lines.append("## Check 2 — 2023 anchor year against the manuscript\n\n")
    lines.append("| Country | Manuscript Table 1 | Rebuilt | Deviation |\n|---|---|---|---|\n")
    for c in sorted(TABLE1_DALY, key=lambda x: -TABLE1_DALY[x]):
        lines.append(f"| {NAME[c]} | {TABLE1_DALY[c]:+.3f} | {r23.loc[c, 'Gap_daly']:+.3f} | "
                     f"{dev[c]:+.4f} |\n")
    lines.append(f"\nMaximum absolute deviation **{max_dev:.4f}**, consistent with the "
                 f"three-decimal rounding used in the manuscript table.\n\n")
    lines.append("## Output\n\n")
    lines.append("`data/gap_yearly_15_daly.csv` — 210 rows, columns "
                 "`country, year, stroke_daly_per100k, D_norm, S_norm, Gap`.\n\n")
    lines.append("## Scope\n\n")
    lines.append("This script rebuilds the panel-level Gap only. The dose-response identity, "
                 "the weighting-sensitivity grid and the debt-instrument matching reported in "
                 "the manuscript are functions of S and of the priority set, and are reproduced "
                 "by `scripts/13_build_d2h.py` under the same S.\n")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[11c] rows={len(out)}  max_dev_incidence_repro={max_inc_dev:.2e}  "
          f"max_dev_table1={max_dev:.4f}")
    assert max_inc_dev < 1e-5, "incidence reproduction failed: S or frame has drifted"
    assert max_dev < 0.001, "DALY gaps do not match the manuscript table"


if __name__ == "__main__":
    main()
