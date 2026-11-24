# Step 11c validation — Gap on the DALY burden metric

Rebuilt from `data/gap_yearly_15.csv` (S side, carried over unchanged) and `data/stroke_burden_rates_15countries_gbd2023.csv` (D side).

## Frame

- `D_norm = minmax(stroke DALY crude rate)` over the pooled 15 countries x 2010-2023 = 210 country-years.
- `S_norm` inherited row by row from Step 11b; S is not recomputed.
- All rates are GBD 2023 crude rates (per 100,000, all ages, both sexes), not age-standardised.

## Check 1 — incidence-basis reproduction

Recomputing the incidence-basis Gap from the archived incidence rate with the same frame reproduces the archived `Gap` column to a maximum absolute deviation of **3.63e-07**, which is the rounding of the archived CSV to six decimals and not a discrepancy. S and the frame have therefore not drifted, and any difference between the two metrics is attributable to D.

## Check 2 — 2023 anchor year against the manuscript

| Country | Manuscript Table 1 | Rebuilt | Deviation |
|---|---|---|---|
| Myanmar | +0.852 | +0.852 | -0.0004 |
| Laos | +0.438 | +0.438 | +0.0000 |
| Indonesia | +0.381 | +0.381 | -0.0004 |
| Vietnam | +0.186 | +0.186 | -0.0001 |
| Cambodia | +0.113 | +0.113 | -0.0002 |
| China | +0.005 | +0.005 | +0.0001 |
| Thailand | -0.047 | -0.047 | +0.0004 |
| Philippines | -0.053 | -0.053 | -0.0004 |
| Malaysia | -0.118 | -0.118 | -0.0003 |
| Brunei | -0.239 | -0.239 | -0.0001 |
| Singapore | -0.420 | -0.420 | +0.0003 |
| Korea | -0.477 | -0.477 | -0.0002 |
| Japan | -0.486 | -0.486 | +0.0001 |
| United Kingdom | -0.691 | -0.691 | -0.0004 |
| United States | -0.800 | -0.800 | -0.0002 |

Maximum absolute deviation **0.0004**, consistent with the three-decimal rounding used in the manuscript table.

## Output

`data/gap_yearly_15_daly.csv` — 210 rows, columns `country, year, stroke_daly_per100k, D_norm, S_norm, Gap`.

## Scope

This script rebuilds the panel-level Gap only. The dose-response identity, the weighting-sensitivity grid and the debt-instrument matching reported in the manuscript are functions of S and of the priority set, and are reproduced by `scripts/13_build_d2h.py` under the same S.
