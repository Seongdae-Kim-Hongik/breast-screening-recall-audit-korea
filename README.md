# Breast screening recall and suspected-cancer judgements across districts of the Republic of Korea, 2011-2024

Analysis code for the manuscript

> Kim S. *Do Korean districts that recall more women at breast screening find more suspected cancers?* Manuscript submitted for publication.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24332133 (v1.0.0).

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected recalls, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/BRRC/sets_BRRC_*.json`, `config_BRRC_std3.json`, `run_std3_chain.sh` | District characteristics with expected directions, forced controls, negative controls, comparison outcomes and model settings (principal model `std3`; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, with crude expected recalls, without 2020, and with care outside the district and hospital beds added) |
| `04_분석/BRRC/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Breast cancer screening results by district of residence (women screened; no abnormality, BI-RADS 1; benign finding, BI-RADS 2; recall/'judgement deferred', BI-RADS 0 and 3; suspected cancer, BI-RADS 4 and 5; existing cancer reported separately), 2011-2024: National Health Insurance Service, Korean Statistical Information Service (KOSIS DT_35007_N017); invited and screened women by district (DT_35007_N009).
- National breast screening results by 5-year age group (DT_35007_N018) and national women screened by age (DT_35007_N010), fetched by `50B_brrc_fetch_N018.py` and `99R_next5d_fetch_cancerscreen.py` (a personal KOSIS API key in `~/.kosis_key` is required; the key is not included).
- Female population by district and 5-year age group: Ministry of the Interior and Safety, resident registration statistics (the 2023 age block of Changwon duplicated the 2022 block and was corrected).
- District covariates: health insurance statistics (clinics, general hospitals, hospital beds, care used outside the district), national health screening (obesity), the Community Health Survey (walking, moderate-to-vigorous physical activity), the national public sports facility register, a harmonised public district panel (tertiary education, basic livelihood security recipients with corrected cells) and KOSIS local indicators (forced and negative controls).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT`, `ST_FBDZIP_CORRECTED` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database).

| Step | Script | Output |
|---|---|---|
| 0 | `99R_next5d_fetch_cancerscreen.py`, `50B_brrc_fetch_N018.py` | District and national screening tables |
| 1 | `99R_next5d_cancerscreen_E.py`, `50F_brrc_counts_fix.py`, `50E_brrc_Estd.py` | District counts joined by code and name (the breast judgement table swaps the codes of two Busan districts relative to the screening table; `50F` joins on both); age-standardised expected recalls and suspicious judgements |
| 2 | `99H_hcuv_build.py`, `99c_extra_canonical_pool_brrc.py` | District characteristics joined by district code |
| 3 | `80_build_disease_panel_v.py BRRC` (`ST_VER=std3`) | Analytic panel |
| 4 | `50K_brrc_likelihood.R` | Likelihood comparison (Poisson, negative binomial, zero-inflated, observation-level effect, binomial, beta-binomial) |
| 5 | `81_fit_inla.R BRRC` | Principal model, negative controls, periods, multiverse (200 random covariate subsets), spatial and residual summaries |
| 6 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `87_window_grid.py` | Period and yearly maps |
| 7 | `88g_sens_prep.py`, `88g_sens_suite.R`, `88h_ppc_varpart.R`, `88k_struct_kh.R`, `89g_sens_combine.py` | Sensitivity analyses (province-by-year effect, likelihood, temporal structure, lags, Spatial+, leave-one-out, Knorr-Held interactions, comparison outcomes) |
| 8 | `50D_brrc_aux.py` | Recall versus suspicious judgements, 2020 stability, between-province variance |
| 8b | `04_분석/BRRC/MS/build/gate_judgement_brrc.py` | National judgement composition by year (BI-RADS categories of the programme) checked against the published programme recall rate |
| 9 | `04_분석/BRRC/MS/build/run_all_jms_brrc.sh` | Manuscript numbers, tables, figures and supplementary material |

The whole chain is `04_분석/BRRC/run_std3_chain.sh`. Software: R 4.6.0, R-INLA 25.10.19, Python 3.9.

## Licence

MIT (see `LICENSE`).
