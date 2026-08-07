# Stroke Rehabilitation Debt-for-Health Allocation — Data & Code Deposit

Companion repository for **Paper 3 (policy / Debt-to-Health)** of the stroke rehabilitation demand research programme (15 economies, 2010–2023):

- *Targeting rehabilitation market failures after WHA79.10: a debt-for-health allocation design across 15 Asia–Pacific and high-income economies* — targeting *Health Policy* (Elsevier).

Sibling deposit (Papers 1 & 2, mechanism and method): [stroke-rehab-demand-dual-pathway-deposit](https://github.com/kongdeyu0819-rgb/stroke-rehab-demand-dual-pathway-deposit).

## Contents

- `data/`
  - `gap_yearly_15.csv` — the market-failure node `Gap = D − S` (panel-relative index) for 15 countries × 14 years (Step 11b).
  - `d2h_scenarios.csv` — three scenarios (S1 baseline; S2 pessimistic, unemployment +2pp) on the 2023 anchor year (Step 13).
  - `d2h_dose_response.csv` — dose-response of the Gap to current-health-expenditure injections (0.25–2.0 pp of GDP, observed window) plus exact closure doses δ* (out-of-sample, illustrative only).
  - `d2h_pt_costing.csv` — physiotherapist-workforce costing against the US density benchmark (71.8 per 100k); PT density is available for 4 of 15 countries, the remainder are labelled as blue-ocean data gaps.
- `scripts/`
  - `11b_build_gap_15countries.py` — Gap construction on the 15-country panel.
  - `13_build_d2h.py` — D2H three-scenario configuration, dose-response and PT costing. **Note (2026-08-07):** the closure-dose coefficient was corrected from 4.0 to 3.0 (the single-component derivative of the three-component supply mean carries a 1/3 factor); previously reported δ* values were overestimated by a factor of 4/3.
  - `paper3_figures.py` — the three paper figures (design logic; 2023 anchor-year Gap; dose-response).
- `outputs/` — validation reports for Step 11b and Step 13 (including honest-limitation statements).
- `figures/` — the three publication figures (300 dpi).

## Provenance

The aggregate panel was constructed from public sources: GBD 2023 (IHME), WHO Global Health Observatory, World Bank World Development Indicators, and IMF World Economic Outlook. WHA79.10 resolution text: World Health Assembly, 23 May 2026.

## Reproducibility

Random seed **3407** is used throughout the wider programme. The Gap is a panel-relative targeting index, not an absolute count of unmet need; scenario elasticities are literature-anchored assumptions; closure doses beyond the observed 0.25–2.0 pp window are illustrative extrapolations.

## License

Code: MIT. Data: subject to the terms of the respective source repositories.
