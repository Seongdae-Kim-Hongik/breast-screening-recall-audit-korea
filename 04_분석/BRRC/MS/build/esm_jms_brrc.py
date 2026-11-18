# esm_jms_brrc.py — BRRC J Med Screening 재투고 보충 자료(Appendix S1·Table S1 전국 판정 구성(게이트)·S2–S5) + STROBE(2026-11-18, esm_brrc 이식).
#  수치는 결과 CSV에서만. 표 제목 쌍점 금지. 보충 번호 = 본문 첫 인용 순서(S1 공변량 → S2 우도 → S3 사양 → S4 핫스팟).
import os, re, json, subprocess, pandas as pd
import numbers_brrc as NB
from build_jms_brrc import N, TX, TITLE as DTITLE, foot_row, GROUPS, METHODS, results, f3
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out_jms"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
J = TX(cite="sup")
def TF(title, header, rows, foot="", fs=8, orient=None):
    (J.new_page(orient) if orient else J.page_break()); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary material</b>"); J.para(f"Supplementary material for the manuscript entitled \"{DTITLE}\"")
J.para("Contents. Appendix S1 (supplementary methods and additional results); Table S1 (national judgement composition); Table S2 (district characteristics); Table S3 (likelihood comparison); Table S4 (alternative specifications); Table S5 (residual hot spots and cold spots).")
MT = pd.read_csv(os.path.join(B, "panel_META_BRRC_std3.csv"), encoding="utf-8-sig").set_index("variable")
imp = lambda v: int(MT.loc[v, "n_imputed_interp"] + MT.loc[v, "n_imputed_sgg_mean"] + MT.loc[v, "n_imputed_year_mean"])
gate = open(os.path.join(B, "data_gate_BRRC_std3_261114.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
vif = MT.vif_final.dropna().sort_values(ascending=False)
AX = N["aux"]; OBY = N["P"].groupby("year")[f"{NB.OB}_raw"].mean().to_dict()
J.page_break(); J.head("Appendix S1. Supplementary methods and additional results", 2)
SM = [("Outcome and denominator.", f"District tables of the national breast cancer screening programme report, for each year and district of residence, the number of women screened and the number in each judgement category. District counts summed to the national totals in every year. "
       f"The 14-year totals were {N['exam_total']:,} examinations, {N['cases_total']:,} recalls ('judgement deferred') and {N['sp_total']:,} examinations judged suspicious for cancer. The district of Sejong, published only as a province-level row, was included in all 14 years."),
      ("Expected recalls.", "Let R(y,a) be the national recall rate in year y and age group a (ten groups: 40–44 to 80–84 and 85 years or older) and U(y,a) the national number of women screened divided by the national female population in that group. "
       "For district d the age weights were w(d,y,a) = F(d,y,a)U(y,a) / Σ_a F(d,y,a)U(y,a), where F is the female resident population, and expected recalls were E(d,y) = S(d,y) Σ_a w(d,y,a)R(y,a), with S the number screened; E was rescaled within each year so that ΣE equalled the observed total. "
       f"The estimated mean age of screened women ranged from {N['exam_age'][0]:.1f} to {N['exam_age'][2]:.1f} years across district-years (median {N['exam_age'][1]:.1f}). Expected suspicious judgements used the same weights with national age-specific rates of that category."),
      ("Covariates.", f"Women aged 40–49 years among women aged 40 years or older came from resident registration. Obesity at health screening was the share of general health-screening participants classified for obesity management. Breast screening uptake was women screened over women invited, by district and year. Clinics, general hospitals, hospital beds and care used outside the district came from health insurance statistics; tertiary education and basic livelihood recipients came from a harmonised public district panel, with recipient shares that collapsed in 2021–2023 in cities with general wards corrected by within-district interpolation. "
       f"The mean district obesity share fell from {OBY[2018]:.1f}% in 2018 to {OBY[2019]:.1f}% in 2019 and changed little thereafter, a step consistent with a change in the screening judgement criteria rather than in obesity; national year effects in every model absorb such common shifts. Cells filled by interpolation or means: obesity {imp(NB.OB)}, other characteristics 0 to {max(imp(v) for v in NB.HYP)}."),
      ("Panel checks before modelling.", f"An automated gate run on the analytic panel before any model was fitted reported {nwarn} flags, all ratio artefacts of standardised columns near zero, real trends over time, the sex ratio above 100 by definition, the post-2020 indicator (constant by design) and districts with no general hospital (true zeros); none concerned keys, outcome counts or denominators. "
       f"Final variance inflation factors were all below 10 (largest {vif.iloc[0]:.1f}, {NB.LAB.get(vif.index[0], vif.index[0]).split(' (')[0].lower() if vif.index[0] in NB.LAB else vif.index[0]})."),
      ("Models.", "R 4.6.0 with R-INLA (one thread) and Python 3.9 for data preparation and figures. Fixed effects had normal priors with mean 0 and precision 4 (intercept precision 0.001). The Besag–York–Mollié 2 district effect used penalised-complexity priors (P(σ > 0.5) = 0.01; P(φ < 0.5) = 2/3) on a 593-edge adjacency graph with island districts linked to the nearest mainland district; year effects used penalised-complexity priors (P(σ > 0.5) = 0.01). "
       f"The multiverse analysis fitted {N['mv_total']} models, each with a random subset of the ten characteristics drawn with a fixed seed.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
ci = N["covid_inter"]; up = ci.get(NB.UP)
J.para("<b>Additional results.</b> " + f"The period from 2020 had no credible main effect ({f3(N['covid_main'])}); among interactions with that period, {sum(1 for v in NB.HYP if ci[v][3])} of ten were credible"
       + (f" (breast screening uptake × period, {f3(up)})" if up and up[3] else "") + ". "
       f"The district standardised recall ratios (SRRs) of recall and of cervical cytological abnormality at the same programme were correlated at ρ = {AX['recall_vs_CXAB_rho']:.2f}. "
       f"The share of the variance of the annual log SRR between provinces averaged {100*AX['between_province_share_logSIR_yearly_mean_min_max'][0]:.0f}% (range {100*AX['between_province_share_logSIR_yearly_mean_min_max'][1]:.0f}%–{100*AX['between_province_share_logSIR_yearly_mean_min_max'][2]:.0f}%).")
# Table S1 전국 판정 구성(판정 구성 대조 게이트, gate_judgement_brrc.py)
JC = pd.read_csv(os.path.join(OUT, "S5_judgement_composition.csv"), encoding="utf-8-sig")
rows = [[str(int(r.year)), f"{int(r.screened):,}".replace(",", " "), f"{r.normal:.2f}", f"{r.benign:.2f}", f"{r.recall:.2f}", f"{r.suspicious:.2f}", f"{r.existing:.2f}", f"{r.recall_plus_susp:.2f}", "–" if pd.isna(r.KJR_RR) else f"{r.KJR_RR:.2f}"] for r in JC.itertuples()]
TF("Table S1 National judgement categories at breast cancer screening by year, Republic of Korea, 2011–2024", ["Year", "Women screened", "No abnormality, %", "Benign, %", "Recall, %", "Suspected cancer, %", "Existing cancer, %", "Recall + suspected, %", "Published recall rate, %<sup>a</sup>"], rows,
   "Categories follow the programme's quality guidelines: no abnormality, BI-RADS 1; benign, BI-RADS 2; recall ('judgement deferred'), BI-RADS 0 and 3; suspected cancer, BI-RADS 4 and 5. The four categories sum to the number screened; women with existing breast cancer are reported separately and expressed per 100 women screened. "
   "Source: national totals of the district judgement tables (Korean Statistical Information Service, DT_35007_N017). BI-RADS, Breast Imaging Reporting and Data System. <sup>a</sup>Recall rate (BI-RADS 0, 3, 4 and 5) of the national programme reported by Kim et al. (Korean J Radiol 2025; 26: 313–323), available for 2011–2020.", fs=7, orient="landscape")
# Table S2
DIR = {NB.F40: "+", NB.OB: "−", NB.TE: "+", NB.UP: "−", NB.CL: "+", NB.GH: "−", NB.BL: "+", NB.WK: "−", NB.MP: "−", NB.FAC: "−"}
SRC = {NB.F40: "Resident registration", NB.OB: "National health screening", NB.TE: "Census (district panel)", NB.UP: "National cancer screening", NB.CL: "Health insurance statistics", NB.GH: "Health insurance statistics", NB.BL: "District panel", NB.WK: "Community Health Survey", NB.MP: "Community Health Survey", NB.FAC: "Sports facility register",
       "urban_population_share": "KOSIS local indicators", "physicians_per_1000": "KOSIS local indicators", "sex_ratio": "KOSIS local indicators", "fiscal_independence": "KOSIS local indicators", "pop80_share": "Resident registration"}
UNIT = {NB.F40: "% of women ≥ 40", NB.OB: "% of participants", NB.TE: "% of adults", NB.UP: "% of invited women", NB.CL: "per 100 000", NB.GH: "per 100 000", NB.BL: "%", NB.WK: "% (age-standardised)", NB.MP: "% (age-standardised)", NB.FAC: "per 100 000",
        "urban_population_share": "%", "physicians_per_1000": "per 1000", "sex_ratio": "men per 100 women", "fiscal_independence": "%", "pop80_share": "%"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = MT.loc[v]; rows.append([f"  {NB.LAB[v].split(' (')[0]}", UNIT[v], SRC[v], f"{int(m.obs_year_min)}–{int(m.obs_year_max)}", ("Forced" if m.role == "forced" else DIR[v]), f"{imp(v)}"])
TF("Table S2 Source, unit, observed years, expected direction and filled cells for each district characteristic, 229 districts, Republic of Korea, 2011–2024", ["Characteristic", "Unit", "Source", "Years", "Direction", "Filled cells"], rows,
   "KOSIS, Korean Statistical Information Service; forced, included in every model. Expected directions were set before any covariate model was fitted. Filled cells of 3206 district-years: interpolation within districts, district means or yearly means. "
   "Sensitivity-only characteristics: share of health care used outside the district of residence and hospital beds per 1000 residents. Negative control exposures (separate model): hit-and-run collisions, a traffic-culture index and fires per 10 000 residents.")
# Table S3
LN = [("poisson", "Poisson"), ("nbinomial", "Negative binomial"), ("zeroinflatedpoisson1", "Zero-inflated Poisson"), ("zeroinflatednbinomial1", "Zero-inflated negative binomial"), ("poisson+obs_iid", "Poisson with observation-level effect"), ("binomial", "Binomial"), ("betabinomial", "Beta-binomial")]
num = lambda x, d=1: "–" if pd.isna(x) or x == float("inf") else f"{x:.{d}f}"
rows = [[lab, num(L["WAIC"]), num(L["DIC"]), num(L["neg_logscore"]), "–" if pd.isna(L["size"]) else f"{L['size']:.1f}"] for k, lab in LN for L in [N["lik"][k]]]
TF("Table S3 Likelihood comparison for recall with forced controls and the same random effects, 3206 district-years, Republic of Korea, 2011–2024", ["Likelihood", "WAIC", "DIC", "−Σ log CPO", "Size"], rows,
   "WAIC, widely applicable information criterion; DIC, deviance information criterion; CPO, conditional predictive ordinate; size, negative binomial size parameter; –, not applicable or not finite. No district-year had zero recalls. "
   "Binomial and beta-binomial models used the number screened as trials with the age-standardised expected proportion as offset. The principal model used the negative binomial likelihood, chosen before characteristics were added by the pre-specified comparison with Poisson; the Poisson model with an observation-level effect was refitted with all characteristics as an alternative specification (Table S4).", fs=8)
# Table S4
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "ICAR district effect"), ("iid_only", "IID district effect"), ("no_spatial", "No district effect"),
         ("C1_poisson_lognormal", "Poisson, observation effect"), ("C2_rw2_year", "RW2 year effect"), ("C3_ar1_year", "AR1 year effect"), ("C4_sido_year_iid", "Province-by-year effect"), ("D1_spatial_plus", "Spatial+-type"),
         ("E1_lag1", "Lag 1 year"), ("E2_lag2", "Lag 2 years"), ("F3_extreme_R7", "Extreme values refilled"), ("H4_odd_years", "Odd years only"), ("H4_even_years", "Even years only"),
         ("sx20", "Without 2020"), ("si", "Care outside district and beds added"), ("s8", "Crude expected recalls"), ("s2", "Share aged ≥ 80 years omitted"), ("s577", "Queen graph, 577 edges"),
         ("bw_twoway", "Between and within components"), ("H1_nco_BRCA", "Breast cancer patients (comparison)"), ("H1_nco_GCA", "Gastric cancer patients (comparison)")]
SS = {**N["s43"], **N["s41"]}
for v in ("s577", "s2", "s8", "sx20", "si"): SS.update({(v, c): t for c, t in N["sens"][v].items()})
SS.update({("principal", c): t for c, t in N["main"].items()})
for v in NB.HYP:
    if v + "__within" in N["bw"]: SS[("bw_twoway", v)] = N["bw"][v + "__within"]
def cell(a, v): t = SS.get((a, v)); return "–" if t is None else (f"{t[0]:.3f}" + ("*" if t[3] else ""))
SH = {NB.F40: "40–49", NB.OB: "Obesity", NB.TE: "Tertiary", NB.UP: "Uptake", NB.CL: "Clinics", NB.GH: "Hospitals", NB.BL: "Recipients", NB.WK: "Walking", NB.MP: "MVPA", NB.FAC: "Sports fac."}
rows = [[lab] + [cell(a, v) for v in NB.HYP] for a, lab in NAMES if any((a, v) in SS for v in NB.HYP)]
TF("Table S4 Rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, 229 districts, Republic of Korea, 2011–2024", ["Specification"] + [SH[v] for v in NB.HYP], rows,
   "Values are rate ratios per 1 standard deviation; *95% credible interval excludes 1; –, not estimated. 40–49, women aged 40–49 years; obesity, obesity at health screening; tertiary, tertiary-educated adults; uptake, breast screening uptake; clinics and hospitals, per 100 000; recipients, basic livelihood recipients. "
   "For the between and within row, values are within-district components. Comparison outcomes were fitted with the same model. ICAR, intrinsic conditional autoregressive; IID, independent and identically distributed; RW2, second-order random walk; AR1, first-order autoregressive. "
   f"Omitting each province or each year: public sports facilities credible in {N['n_drop_cred'][NB.FAC][0]} of {N['n_drop_cred'][NB.FAC][1]} fits; the other characteristics in {sum(N['n_drop_cred'][v][0] for v in NB.HYP if v != NB.FAC)} of {sum(N['n_drop_cred'][v][1] for v in NB.HYP if v != NB.FAC)}.", fs=7, orient="landscape")
# Table S5
EN = {"서울시": "Seoul", "부산시": "Busan", "대구시": "Daegu", "인천시": "Incheon", "광주시": "Gwangju", "대전시": "Daejeon", "울산시": "Ulsan", "세종시": "Sejong", "경기도": "Gyeonggi-do", "강원도": "Gangwon-do", "충청북도": "Chungcheongbuk-do",
      "충청남도": "Chungcheongnam-do", "전라북도": "Jeollabuk-do", "전라남도": "Jeollanam-do", "경상북도": "Gyeongsangbuk-do", "경상남도": "Gyeongsangnam-do", "제주도": "Jeju-do"}
ROM = json.load(open(os.path.join(HERE, "district_romanization_all.json"), encoding="utf-8"))
S6 = N["s6"].copy(); S6["sido"] = S6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
rows = []
for cls, lab in (("hotspot", "Hot spots"), ("coldspot", "Cold spots")):
    q = S6[S6["class"] == cls].sort_values(["sido", "RR"], ascending=[True, cls != "hotspot"]); rows.append(["__H__", f"{lab} ({len(q)})"])
    for r in q.itertuples(): rows.append([f"  {EN[r.sido]}", ROM[r.fbd_region], f"{r.RR:.2f} ({r.lo:.2f}–{r.hi:.2f})", f"{r.P_gt1:.3f}", f"{r.SIR_obs:.2f}"])
TF("Table S5 Residual hot spots and cold spots of breast screening recall, 229 districts, Republic of Korea, 2011–2024", ["Province", "District", "Residual spatial RR (95% CrI)", "P(RR > 1)", "Observed SRR"], rows,
   "RR, rate ratio from the district effect of the principal model; CrI, credible interval; SRR, standardised recall ratio (observed over age-standardised expected recalls) over 14 years. Hot spots: posterior probability of RR > 1 above 0.95; cold spots: below 0.05. Exploratory; not adjusted for multiple comparisons.", fs=7, orient="portrait")
assert not any(re.search(r"[가-힣]", str(c)) for r in rows for c in r[1:] if r[0] != "__H__")
ps = os.path.join(OUT, "Supplementary_Material_JMS_BRRC.docx"); J.doc_title = "Supplementary material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_brrc_esmj", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
# STROBE
MH = [x[0] for x in METHODS]; RH = [x[0] for x in results()]
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"),
      ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}; {MH[1]}"), ("Participants", "6", f"Methods, {MH[1]} (all women screened; ecological)"),
      ("Variables", "7", f"Methods, {MH[2]}; {MH[3]}; Supplementary Table S2"), ("Data sources/measurement", "8", f"Methods, {MH[1]}; Supplementary Appendix S1; Supplementary Table S1"),
      ("Bias", "9", f"Methods, {MH[4]}; Supplementary Table S4"), ("Study size", "10", f"Methods, {MH[0]} (all 229 districts)"), ("Quantitative variables", "11", f"Methods, {MH[3]}"),
      ("Statistical methods", "12", f"Methods, {MH[4]}; Supplementary Appendix S1; Supplementary Table S3"), ("Participants (flow)", "13", "Results, first paragraph; Fig. 1 (no exclusions)"),
      ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}; Table 1; Fig. 2"),
      ("Main results", "16", f"Results, {RH[1]}; {RH[2]}; Table 2; Figs. 3–5"), ("Other analyses", "17", f"Results, {RH[3]}; {RH[4]}; Supplementary Tables S3–S5"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", "Discussion, third paragraph"), ("Interpretation", "20", "Discussion, second paragraph"), ("Generalisability", "21", "Conclusions"),
      ("Other information (funding, code)", "22", "Statements and Declarations (Funding; Data availability)")]
K = TX(cite="sup"); K.para("<b>STROBE checklist</b>"); K.para(f"Manuscript \"{DTITLE}\"")
K.table_fit("STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(K, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology. Section names refer to the main manuscript and the supplementary material.", 8, 12)
pk = os.path.join(OUT, "STROBE_Checklist_JMS_BRRC.docx"); K.doc_title = "STROBE checklist"; K.save(pk)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_brrc_esmj", "--convert-to", "pdf", "--outdir", OUT, pk], check=True, capture_output=True)
print("saved", os.path.basename(pk))
