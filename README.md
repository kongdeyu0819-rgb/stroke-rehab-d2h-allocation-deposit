# Stroke Rehabilitation Debt-for-Health Allocation — Data & Code Deposit

Companion repository for **Paper 3 (policy / Debt-to-Health)** of the stroke rehabilitation demand research programme (15 economies, 2010–2023):

- *Disease-sensitive financing-gap prioritisation for rehabilitation planning: a reproducible pipeline and debt-for-health allocation across 15 high-income, middle-income and low-income economies*

Sibling deposit (Papers 1 & 2, mechanism and method): [stroke-rehab-demand-dual-pathway-deposit](https://github.com/kongdeyu0819-rgb/stroke-rehab-demand-dual-pathway-deposit).

## Burden metric — read this first

The published analysis uses the **stroke DALY crude rate** as the demand term `D`. An earlier version of the work used the **stroke incidence rate scaled by a fixed factor** (Step 11b). Both share the same supply index `S` and the same min–max frame (15 countries × 2010–2023 = 210 country-years), so the two panels differ only in the burden metric.

| Analysis | Demand term | Gap panel | Script |
|---|---|---|---|
| Primary (manuscript Table 1) | Stroke DALY crude rate, GBD 2023 | `data/gap_yearly_15_daly.csv` | `scripts/11c_build_gap_daly.py` |
| Earlier construction (metric-sensitivity comparator) | Stroke incidence × 0.80, GBD 2023 | `data/gap_yearly_15.csv` | `scripts/11b_build_gap_15countries.py` |

Reproducing the manuscript's Table 1 requires only the two archived CSVs and Step 11c; the incidence panel is retained because the manuscript reports it as a metric-sensitivity comparator. Step 11c reproduces the archived incidence-basis `Gap` column from the archived incidence rate to 3.6 × 10⁻⁷ (six-decimal CSV rounding), which confirms that `S` and the frame have not drifted between the two constructions.

## Contents

- `data/`
  - `gap_yearly_15.csv` — Step 11b panel, incidence basis: `Gap = D_norm − S_norm` for 15 countries × 14 years, with the supply components and `S_index`.
  - `gap_yearly_15_daly.csv` — Step 11c panel, DALY basis (primary analysis): `D_norm`, `S_norm`, `Gap` per country-year.
  - `stroke_burden_rates_15countries_gbd2023.csv` — GBD 2023 crude rates per 100,000 for the 15 economies, 2010–2023, all ages, both sexes, no age standardisation: stroke incidence, DALY, YLD and prevalence. This is the demand-side input; it is redistributed here so that the panel can be rebuilt without the full GBD download.
  - `d2h_scenarios.csv` — three scenarios (S1 baseline; S2 pessimistic, unemployment +2pp) on the 2023 anchor year (Step 13).
  - `d2h_dose_response.csv` — dose-response of the Gap to current-health-expenditure injections (0.25–2.0 pp of GDP, observed window) plus exact closure doses δ* (out-of-sample, illustrative only).
  - `d2h_pt_costing.csv` — physiotherapist-workforce costing against the US density benchmark (71.8 per 100k); PT density is available for 4 of 15 countries, the remainder are labelled as blue-ocean data gaps.
- `scripts/`
  - `11b_build_gap_15countries.py` — Gap construction on the incidence basis (earlier version).
  - `11c_build_gap_daly.py` — Gap construction on the DALY basis (primary analysis), with a built-in reproduction check. Run: `python scripts/11c_build_gap_daly.py`.
  - `11d_extract_gbd_rates.py` — regenerates `data/stroke_burden_rates_15countries_gbd2023.csv` from a GBD 2023 Results Tool export. Not needed unless the rate table is being rebuilt from source; the GBD download itself is not redistributed here.
  - `13_build_d2h.py` — D2H three-scenario configuration, dose-response and PT costing. **Note (2026-08-07):** the closure-dose coefficient was corrected from 4.0 to 3.0 (the single-component derivative of the three-component supply mean carries a 1/3 factor); previously reported δ* values were overestimated by a factor of 4/3.
  - `paper3_figures.py` — the three paper figures (design logic; 2023 anchor-year Gap; dose-response).
- `outputs/` — validation reports for Step 11b, Step 11c and Step 13, including honest-limitation statements.
- `figures/` — the three publication figures (300 dpi).

## Provenance

The aggregate panel was constructed from public sources: GBD 2023 (IHME), WHO Global Health Observatory, World Bank World Development Indicators, and IMF World Economic Outlook. Burden rates are GBD 2023 crude rates for cause = stroke, metric = rate, age = all ages, sex = both; the 15 locations are the ten ASEAN member states plus China, Japan, Korea, and the United States and United Kingdom (the last two enter as reference points at the upper end of the normalisation frame and as the workforce-density benchmark, not as policy targets). WHA79.10 resolution text: World Health Assembly, 23 May 2026.

## Reproducibility

Random seed **3407** is used throughout the wider programme. The Gap is a panel-relative targeting index, not an absolute count of unmet need: it ranks demand against supply within the panel and is not comparable to counts of unmet need derived from external norms. Scenario elasticities are literature-anchored assumptions; closure doses beyond the observed 0.25–2.0 pp window are illustrative extrapolations.

## Version history

- **1.1.0** — adds the DALY-basis Gap panel (Step 11c) and the 15-country GBD 2023 rate table, matching the primary analysis of the manuscript. The incidence-basis panel is unchanged and retained as the metric-sensitivity comparator.
- **1.0.2** — closure-dose coefficient correction (4.0 → 3.0).
- **1.0.0** — initial deposit.

## License

Code: MIT. Data: subject to the terms of the respective source repositories.
