# build_jms_brrc.py — BRRC Journal of Medical Screening 재투고 원고(2026-11-18, build_er_brrc.py 이식; EurRad EURA-D-26-06328 데스크 리젝 11/17).
#  JMS 규정(journals.sagepub.com/author-instructions/MSC, 11/18 크롬 확인): 원저 본문 ≤4,000(초록·표·그림·참고문헌 제외), 구조 초록 ≤250(Objectives/Setting/Methods/Results/Conclusions), 키워드 ≥4,
#   구조 Abstract·Introduction·Methods·Results·Discussion·Conclusions, Acknowledgements 뒤 Author contributions, 끝에 'Statements and Declarations'(Ethical considerations·Consent to participate·Consent for publication·
#   Declaration of conflicting interest·Funding·Data availability, 해당 없으면 'Not applicable'), Sage Vancouver, 그림 300 dpi 이상, EQUATOR 체크리스트(STROBE) 업로드, 단일 익명, 저자 추천 심사자 받지 않음, 요금 없음.
#  판정 구성 게이트(17 KIDS 교훈) 반영: BI-RADS 매핑·4범주+기존 암환자·전국 판정 구성 Table S1.
import os, re, json, subprocess, sys
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
from british import brit
import numbers_brrc as NB
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out_jms"); os.makedirs(OUT, exist_ok=True)
N = NB.load(); REFS = json.load(open(os.path.join(HERE, "refs_brrc.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "02_manuscript_jms.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = "Do Korean districts that recall more women at breast screening find more suspected cancers?"
KEYWORDS = "Breast cancer screening; mammography; recall; false-positive results; quality assurance; spatial analysis"
assert ":" not in TITLE and len(TITLE.split()) <= 20
ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_STATEMENT = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. The author reviewed and edited all output and takes full responsibility for the content of this publication."
IRB = "7002340-202511-HR-012"; IRB2 = "7002340-202611-HR-040"
def data_statement(): return (f"All source data are publicly available aggregate statistics of the National Health Insurance Service and the Ministry of the Interior and Safety, published through the Korean Statistical Information Service. "
                             f"The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")
f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
def rr(t): return f"rate ratio [RR] {t[0]:.3f}, 95% credible interval [CrI] {t[1]:.3f}–{t[2]:.3f}" if False else f"RR {t[0]:.3f}, 95% CrI {t[1]:.3f}–{t[2]:.3f}"
pct = lambda x: f"{100*x:.1f}%"
def rr4(t): return f"RR {t[0]:.3f}, 95% CrI {t[1]:.4f}–{t[2]:.3f}" if round(t[1], 3) == 1.0 else rr(t)
fmt = lambda x: f"{x:,}".replace(",", " ")
AX = N["aux"]; T1 = N["T1"]; AR = N["agerate"]
import pandas as pd
JC = pd.read_csv(os.path.join(OUT, "S5_judgement_composition.csv"), encoding="utf-8-sig").set_index("year")   # gate_judgement_brrc.py
EN = {"서울시": "Seoul", "경기도": "Gyeonggi-do", "인천시": "Incheon", "강원도": "Gangwon-do", "충청남도": "Chungcheongnam-do", "충청북도": "Chungcheongbuk-do", "전라남도": "Jeollanam-do", "전라북도": "Jeollabuk-do",
      "경상남도": "Gyeongsangnam-do", "경상북도": "Gyeongsangbuk-do", "부산시": "Busan", "대구시": "Daegu", "광주시": "Gwangju", "대전시": "Daejeon", "울산시": "Ulsan", "세종시": "Sejong", "제주도": "Jeju-do"}
def top(d, k=4): l = [f"{EN[a]} ({b})" for a, b in list(d.items())[:k]]; return ", ".join(l[:-1]) + " and " + l[-1]
HYP = NB.HYP; M = N["main"]
n_null = sum(1 for v in HYP if not M[v][3])
q = N["ppv_q"]

ABSTRACT = [
 ("Objectives", "To test whether the district geography of recall at national breast cancer screening is accounted for by the age mix and by density-related, supply, deprivation and physical activity characteristics of districts."),
 ("Setting", f"National breast cancer screening programme, all {N['n_districts']} districts of the Republic of Korea, 2011–2024."),
 ("Methods", f"Ecological study of published aggregate data on {fmt(N['exam_total'])} screening mammograms. Recall ('judgement deferred', Breast Imaging Reporting and Data System categories 0 and 3) was age-standardised with national age-specific recall rates. "
  "Bayesian spatial negative binomial models estimated associations with ten pre-specified district characteristics. District recall was compared with examinations judged suspicious for cancer."),
 ("Results", f"Of all examinations, {pct(N['cases_total']/N['exam_total'])} were recalled, falling from {T1['W1_2011-15']['rate']:.1f}% in 2011–2015 to {T1['W3_2020-24']['rate']:.1f}% in 2020–2024. "
  f"District standardised recall ratios ranged from {T1['ALL']['p10']:.2f} to {T1['ALL']['p90']:.2f} (10th–90th percentile) and were nearly unchanged by age-standardisation (Spearman ρ {N['rho_crude_std']:.2f}). "
  f"Residual hot spots clustered in the capital region and cold spots in the south. Nine of ten pre-specified characteristics had credible intervals including 1; public sports facilities per 100 000 were associated with higher recall (rate ratio {M[NB.FAC][0]:.3f}, 95% credible interval {M[NB.FAC][1]:.3f}–{M[NB.FAC][2]:.3f}), opposite to expectation, and post hoc decomposition showed a within-district but no between-district association. Recall was not correlated with suspicious judgements (ρ {AX['recall_vs_suspicion_rho']:.2f}); suspicious judgements per 1000 recalls were {q['Q1']['median']:.1f} in the lowest and {q['Q4']['median']:.1f} in the highest recall quarter."),
 ("Conclusions", "District recall formed a stable spatial pattern that persisted after adjustment for the measured district characteristics and was not accompanied by more suspicious judgements."),
]
KEYPOINTS = [
 ("Question", "Is uneven recall across Korean districts at national breast screening accounted for by the age mix and measured characteristics of the women's districts?"),
 ("Findings", "Age-standardisation barely changed the district map, substantial spatial variation remained after adjustment for measured characteristics, and higher-recall districts recorded no more suspicious judgements."),
 ("Clinical relevance statement", "Breast screening recall varied by region beyond the measured composition of screened women, so regional audit linking recall to reading facilities and confirmed cancers is needed to tell avoidable work-up from greater detection."),
]
ABBR = [("CrI", "Credible interval"), ("INLA", "Integrated nested Laplace approximation"), ("RR", "Rate ratio"), ("SRR", "Standardised recall ratio (observed over age-standardised expected recalls)"), ("WAIC", "Widely applicable information criterion")]

c40 = lambda y: AR[(y, "40-44")]; c85 = lambda y: AR[(y, "85+")]
METHODS = [
("Study design and ethics",
 f"The Institutional Review Board of Hongik University approved this retrospective ecological study ({IRB}; continuing review {IRB2}) and waived informed consent because only published aggregate statistics were used; the study followed the Declaration of Helsinki and is reported according to the STROBE statement [@vonelm2007strengthening]. "
 f"It covered all {N['n_districts']} districts (urban wards, cities and counties) of the Republic of Korea, harmonised to 2024 boundaries, from January 2011 to December 2024 ({fmt(N['n_rows'])} district-years). No district-year was excluded."),
("Screening programme and data",
 "The national programme invites women aged 40 years or older to biennial mammography [@suh2017trends; @kim2025biennial]. Its published statistics place each examination in one of four judgement categories defined by the programme's quality guidelines: no abnormality (Breast Imaging Reporting and Data System [BI-RADS] category 1), benign finding (category 2), recall ('judgement deferred', additional evaluation required; categories 0 and 3) and suspected breast cancer (categories 4 and 5) [@kim2025biennial]; women with existing breast cancer are reported separately. "
 f"The category definitions did not change during the study period. Nationally, recall fell from {JC.loc[2011,'recall']:.1f}% of examinations in 2011 to {JC.loc[2024,'recall']:.1f}% in 2024 while benign findings rose from {JC.loc[2011,'benign']:.1f}% to {JC.loc[2024,'benign']:.1f}%, and suspected cancer stayed between {JC.suspicious.min():.2f}% and {JC.suspicious.max():.2f}%; recall plus suspected cancer agreed with the published programme recall rate within {JC.diff_pp.abs().max():.1f} percentage points in every year from 2011 to 2020 [@kim2025biennial] (Supplementary Table S1). The decline accelerated after 2017 [@kim2025biennial]; year effects in every model and refits in three periods allowed for this change. "
 "Annual numbers of women screened and of each category by district of residence, national numbers by 5-year age group (40–44 to 85 years or older), and national numbers screened by age came from the National Health Insurance Service through the Korean Statistical Information Service; female populations by district and 5-year age group came from resident registration. "
 "District counts were linked to resident populations by administrative code only, national age-specific rates were applied by age group and year, and district totals were checked against national totals in every year (Figure 1)."),
("Outcome and expected recalls",
 "The outcome was the annual number of recalled examinations and the denominator the number of women screened. District tables do not report age, so the age mix of each district's screened women was estimated by weighting its female population in each age group by the national ratio of women screened to women resident in that group. "
 "Expected recalls were the number screened multiplied by the national age-specific recall rates for that year averaged over these weights (indirect standardisation), rescaled so that expected and observed totals matched each year (formula in Supplementary Appendix S1). The ratio of observed to expected recalls is the standardised recall ratio (SRR). "
 "Crude expected recalls (number screened multiplied by the national annual rate) were used in a sensitivity analysis. Examinations judged suspicious for cancer were standardised with the same weights."),
("District characteristics",
 "Ten characteristics were fixed before any model was fitted, each with an expected direction (Supplementary Table S2). "
 "Density-related composition was represented by the share of women aged 40–49 years among women aged 40 years or older (expected to raise recall because greater density lowers specificity and is common before menopause) [@carney2003individual], obesity at national health screening (expected to lower recall through less dense tissue, although obesity has also been associated with more recalls) [@elmore2004the] and the tertiary-educated share (expected to raise recall through later and fewer births, which are associated with greater density) [@odriscoll2024reproductive; @al2025education]; these were treated as hypotheses about district proxies, not as measures of density. "
 "The screening setting was represented by breast screening uptake (expected to lower recall because more women have prior mammograms) [@hubbard2011cumulative], clinics per 100 000 residents (expected to raise it through low-volume reading) and general hospitals per 100 000 (expected to lower it) [@cornford2021optimum]; deprivation was represented by the share of basic livelihood security recipients (expected to raise it) [@goldman2011accuracy]. "
 "Physical activity, a common pathway in this district series, was represented by age-standardised walking and moderate-to-vigorous physical activity from the Community Health Survey and by public sports facilities per 100 000 residents, all expected to lower recall through lower breast density, although evidence that activity lowers density is inconsistent [@yaghjyan2012physical; @lee2024physical]. "
 "Five controls were forced into every model: urban population share, physicians per 1000 residents, sex ratio, fiscal autonomy and the share aged 80 years or older. Three negative control exposures with no plausible effect on recall (hit-and-run collisions, a traffic-culture index and fires) were fitted separately [@lipsitch2010negative]. All characteristics were standardised to mean 0 and standard deviation 1."),
("Statistical analysis",
 f"Five likelihoods (Poisson, negative binomial, zero-inflated Poisson, zero-inflated negative binomial and Poisson with an observation-level effect) and binomial and beta-binomial models were compared with the same random effects (Supplementary Table S3). The principal model was negative binomial, chosen by the pre-specified rule of a lower WAIC than Poisson for the forced-control model [@gelman2014understanding]; the Poisson model with an observation-level effect, which had the lowest WAIC, was refitted with all characteristics as an alternative. "
 "The principal model had an offset of log expected recalls, a Besag–York–Mollié 2 district effect with penalised-complexity priors [@riebler2016an] and random-walk and independent year effects, fitted by INLA in R 4.6.0 [@rue2009approximate]. "
 "RRs per 1 standard deviation are reported with 95% CrIs; an association was called credible when its interval excluded 1, and no multiplicity correction was applied. Residual hot and cold spots were districts whose posterior probability of a residual spatial RR above 1 exceeded 0.95 or fell below 0.05 (exploratory). "
 f"Robustness was assessed in {N['mv_total']} models with randomly drawn subsets of the ten characteristics (robust when credible in at least 75% of the models containing the characteristic, with at least 95% sign agreement) [@steegen2016increasing]; four Knorr-Held space-time interactions [@knorrheld2000bayesian]; refits in three periods; alternative likelihood, temporal structure, lags and spatial confounding adjustment; omission of each province and each year; crude expected recalls, a different adjacency graph and omission of the share aged 80 years or older (Supplementary Table S4).",
 "Facility identifiers are not published, so sensitivity to variation shared by neighbouring districts was assessed with an independent province-by-year effect, and a second model added the share of health care used outside the district of residence and hospital beds per 1000 residents. "
 "The 2020 decline in attendance was addressed by refitting without 2020 and by testing interactions of each characteristic with the period from 2020. "
 "Treated breast cancer patients and treated gastric cancer patients in the national health insurance system (age-standardised) were fitted with the same model as comparison outcomes. "
 "Associations opposite to the expected direction were examined post hoc with the existing fits only (between-district and within-district components, lags, refits by period and spatial confounding adjustment), without changing the principal model. "
 "As an auxiliary descriptive analysis, 14-year district SRRs of recall were compared by Spearman correlation with those of suspicious judgements, of treated breast cancer and of cervical cytological abnormality at the same programme (atypical cells or worse among women screened), and the ratio of suspicious judgements to recalls was summarised by quarter of recall SRR."),
]

def results():
    C4 = lambda v: N["s41"][("C4_sido_year_iid", v)]; X20 = lambda v: N["sens"]["sx20"][v]; SI = lambda v: N["sens"]["si"][v]; S8 = lambda v: N["sens"]["s8"][v]; PO = lambda v: N["s41"][("C1_poisson_lognormal", v)]
    ncred_c4 = sum(1 for v in HYP if C4(v)[3]); ncred_x20 = sum(1 for v in HYP if X20(v)[3]); ncred_si = sum(1 for v in HYP if SI(v)[3]); ncred_s8 = sum(1 for v in HYP if S8(v)[3]); ncred_po = sum(1 for v in HYP if PO(v)[3])
    w2 = [v for v in HYP if v != NB.FAC and N["win"][(v, "W2_2016-19")][3]]; ci = N["covid_inter"]; cin = [v for v in HYP if ci[v][3]]
    nm = lambda v: NB.LAB[v].split(" (")[0].lower().replace("per 100 000", "").strip()
    NC = lambda o: [v for v in HYP if N["nco"][(o, v)][3]]
    win_txt = ("In period-specific refits, " + " and ".join(f"{nm(v)} ({rr(N['win'][(v, 'W2_2016-19')])})" for v in w2) + (" were" if len(w2) > 1 else " was") + " credible in 2016–2019 only. ") if w2 else "No characteristic was credible in any of the three periods. "
    WORD = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
    R = [
    ("Screening, recall and age",
     f"All {N['n_districts']} districts contributed 14 years ({fmt(N['n_rows'])} district-years; Figure 1), with {fmt(N['exam_total'])} screening examinations and {fmt(N['cases_total'])} recalls ({pct(N['cases_total']/N['exam_total'])}; Table 1). "
     f"The national recall rate fell from {N['nat_year'].loc[2011,'rate_pct']:.1f}% in 2011 to {N['nat_year'].loc[2024,'rate_pct']:.1f}% in 2024, and the number screened fell from {fmt(int(N['nat_year'].loc[2019,'exam']))} in 2019 to {fmt(int(N['nat_year'].loc[2020,'exam']))} in 2020 (Figure 2a). "
     f"Recall declined with age, from {100*c40(2011):.1f}% at 40–44 years to {100*c85(2011):.1f}% at 85 years or older in 2011 and from {100*c40(2024):.1f}% to {100*c85(2024):.1f}% in 2024 (Figure 2b). "
     f"Age-standardised expected recalls differed from crude expected recalls by a factor of {N['E_ratio'][0]:.2f}–{N['E_ratio'][2]:.2f}; the 14-year district SRRs from the two were correlated at ρ = {N['rho_crude_std']:.2f}, and the correlation of the SRR with the share of women aged 40–49 years fell from {N['rho_f40_crude']:.2f} to {N['rho_f40_std']:.2f} after standardisation."),
    ("District pattern",
     f"Age-standardised district SRRs ranged from {T1['ALL']['p10']:.2f} to {T1['ALL']['p90']:.2f} between the 10th and 90th percentiles (Figure 3a). Moran's I of the pooled log SRR was {N['moran_pooled']:.2f}, and annual values ranged from {N['moran_year'][0]:.2f} to {N['moran_year'][1]:.2f}. "
     f"District rankings were stable: Spearman correlations of SRRs between 2011–2015, 2016–2019 and 2020–2024 ranged from {N['rho_win'][0]:.2f} to {N['rho_win'][1]:.2f}, and between adjacent years from {min(AX['SIR_rank_rho_adjacent_years'].values()):.2f} to {max(AX['SIR_rank_rho_adjacent_years'].values()):.2f}. "
     f"In the principal model the structured share of the district effect (φ) was {N['phi'][0]:.2f} (95% CrI {N['phi'][1]:.2f}–{N['phi'][2]:.2f}), and the residual Moran's I was {N['moran_resid']:.2f}. "
     f"There were {N['n_hot']} residual hot spots, mainly in {top(N['hot_by_sido'])}, and {N['n_cold']} cold spots, mainly in {top(N['cold_by_sido'])} (Figure 3b, c; Supplementary Table S5). Between-province differences accounted for {100*AX['between_province_share_logSIR_pooled']:.0f}% of the variance of the pooled log SRR."),
    ("District characteristics",
     f"In the principal model, nine of the ten characteristics had 95% CrIs that included 1 (Table 2); their RRs per 1 standard deviation lay between {min(M[v][0] for v in HYP if v != NB.FAC):.3f} and {max(M[v][0] for v in HYP if v != NB.FAC):.3f}. "
     f"Public sports facilities per 100 000 were associated with higher recall ({rr(M[NB.FAC])}), opposite to the expected direction; urban population share and fiscal autonomy among the forced controls were also associated with higher recall ({rr(M['urban_population_share'])}; {rr(M['fiscal_independence'])}). "
     f"The facility association was credible in all {N['mv']['public_sports_facilities_per_100k']['n_specs']} covariate subsets that contained it (Supplementary Table S4), with the Poisson model with an observation-level effect ({rr(PO(NB.FAC))}), with a province-by-year effect ({rr(C4(NB.FAC))}) and after omission of each province and each year, whereas no other characteristic was credible in any subset. None of the negative control exposures was credible. "
     + win_txt),
    ("Public sports facilities (post hoc)",
     f"In the 14-year district means, public sports facilities per 100 000 were inversely correlated with the recall SRR (ρ = {N['fac_rho']['srr']:.2f}) and strongly correlated with urban population share (ρ = {N['fac_rho']['urb']:.2f}) and population size (ρ = {N['fac_rho']['pop']:.2f}). "
     f"When the association was split into components, the between-district component was not associated with recall ({rr(N['bw'][NB.FAC + '__between'])}), whereas the within-district component was ({rr(N['bw'][NB.FAC + '__within'])}). "
     f"The association weakened with Knorr-Held space-time interactions that allow district-specific trends (type II {rr(N['s43'][('KH_typeII', NB.FAC)])}; type IV {rr(N['s43'][('KH_typeIV', NB.FAC)])}), was present with 1-year and 2-year lags ({rr(N['s41'][('E1_lag1', NB.FAC)])}; {rr(N['s41'][('E2_lag2', NB.FAC)])}) and was not seen for treated breast cancer ({rr(N['nco'][('BRCA', NB.FAC)])}) or treated gastric cancer ({rr4(N['nco'][('GCA', NB.FAC)])}). "
     f"In period refits the association was credible in 2016–2019 ({rr(N['win'][(NB.FAC, 'W2_2016-19')])}) and 2020–2024 ({rr(N['win'][(NB.FAC, 'W3_2020-24')])}) but not in 2011–2015 ({rr(N['win'][(NB.FAC, 'W1_2011-15')])}). Facilities per 100 000 rose from {N['fac_year'][2011]:.1f} in 2011 to {N['fac_year'][2024]:.1f} in 2024 on average."),
    ("Recall and suspicious judgements",
     f"Over the 14 years, {fmt(N['sp_total'])} examinations ({100*N['sp_total']/N['exam_total']:.2f}%) were judged suspicious for cancer. District SRRs of recall and of suspicious judgements were not correlated (ρ = {AX['recall_vs_suspicion_rho']:.2f}; Figure 4a). "
     f"Suspicious judgements per 1000 recalls had a median of {q['Q1']['median']:.1f}, {q['Q2']['median']:.1f}, {q['Q3']['median']:.1f} and {q['Q4']['median']:.1f} from the lowest to the highest quarter of recall SRR (Figure 4b). "
     f"The recall SRR was correlated with the SRR of treated breast cancer (ρ = {AX['recall_vs_BRCA_treated_rho']:.2f}) and of cervical cytological abnormality (ρ = {AX['recall_vs_CXAB_rho']:.2f}), whereas suspicious judgements were not correlated with treated breast cancer (ρ = {AX['suspicion_vs_BRCA_treated_rho']:.2f})."),
    ("Province-level variation and 2020",
     f"With a province-by-year effect, {WORD[ncred_c4]} of the ten characteristics {'was' if ncred_c4 in (0, 1) else 'were'} credible (public sports facilities), and adding care outside the district and hospital beds left {WORD[ncred_si]} credible (Figure 5). "
     f"Without 2020, {WORD[ncred_x20]} {'was' if ncred_x20 in (0, 1) else 'were'} credible (public sports facilities), and the period from 2020 had no credible main effect ({rr(N['covid_main'])}); "
     + (("among interactions with that period, only that of " + " and ".join(f"{nm(v)} ({rr(ci[v])})" for v in cin) + " was credible. ") if cin else "no interaction with that period was credible. ") +
     f"District SRRs in 2020 were correlated with those in 2019 (ρ = {AX['SIR_rank_rho_2019_2020']:.2f}) and 2021 (ρ = {AX['SIR_rank_rho_2020_2021']:.2f}), and the 2020 fall in the number screened (median {AX['exam_drop_2020_median_P10_P90_pct'][0]:.1f}%) was not correlated with the change in SRR (ρ = {AX['exam_drop_vs_logSIR_change_2020_rho']:.2f}). "
     f"With crude expected recalls, the share of women aged 40–49 years had {'a credible' if S8(NB.F40)[3] else 'no credible'} association ({rr(S8(NB.F40))}), and public sports facilities {'remained' if S8(NB.FAC)[3] else 'were not'} credible ({rr(S8(NB.FAC))})."),
    ]
    return R

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def ref(k):   # Sage Vancouver: 저자 3명 넘으면 3명 + et al., 제목. 학술지 약어 연도; 권: 쪽.
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}, {r['url']} ({r['year']}, accessed {r['accessed']})."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 3 else ", ".join(au[:3]) + ", et al."
    a = a if a.endswith(".") else a + "."
    t = r["title"].rstrip(".")
    s = f"{a} {t}. {r['journal']} {r['year']}"
    if r.get("vol"): s += f"; {r['vol']}"
    if r.get("pages"): s += f": {r['pages'].replace('-', '–')}"
    return s + "."

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = brit(text); text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1 = [(NB.F40, "Women aged 40–49 years, % of women ≥ 40"), (NB.OB, "Obesity at health screening, %"), (NB.TE, "Tertiary-educated adults, %"), (NB.UP, "Breast screening uptake, %"),
        (NB.CL, "Clinics per 100 000"), (NB.GH, "General hospitals per 100 000"), (NB.BL, "Basic livelihood recipients, %"), (NB.WK, "Walking, %"), (NB.MP, "Moderate-to-vigorous physical activity, %"), (NB.FAC, "Public sports facilities per 100 000"), ("pop80_share", "Population aged ≥ 80 years, %")]
WC = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "ALL"]; WH = ["2011–2015", "2016–2019", "2020–2024", "2011–2024"]
def table1():
    rows = [["__H__", "Screening and recall"], ["  District-years, no."] + [fmt(T1[c]['n']) for c in WC], ["  Screening examinations, no."] + [fmt(T1[c]['exam']) for c in WC],
            ["  Recalls, no."] + [fmt(T1[c]['cases']) for c in WC], ["  Recall, % of examinations"] + [f"{T1[c]['rate']:.1f}" for c in WC],
            ["  District SRR, median (P10–P90)<sup>a</sup>"] + [f"{T1[c]['med']:.2f} ({T1[c]['p10']:.2f}–{T1[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1:
        mx = max(abs(T1[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T1[c]['cov'][v][0]:.{dp}f} ({T1[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("P10–P90, 10th–90th percentile; SD, standard deviation; SRR, standardised recall ratio. <sup>a</sup>Observed over age-standardised expected recalls summed over the period. "
            "Characteristics are district-year means; the other forced controls are listed in Supplementary Table S2.")
    return (f"Table 1 Screening, recall and district characteristics, {N['n_districts']} districts, Republic of Korea, 2011–2024", ["Characteristic"] + WH, rows, foot)
GROUPS = [("Density-related composition", [NB.F40, NB.OB, NB.TE]), ("Screening and reading setting", [NB.UP, NB.CL, NB.GH]), ("Deprivation", [NB.BL]), ("Physical activity", [NB.WK, NB.MP, NB.FAC]), ("Forced controls", NB.FORCED)]
def table2():
    rows = []
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = M[v]; mv = N["mv"].get(v); c4 = N["s41"].get(("C4_sido_year_iid", v)); x = N["sens"]["sx20"].get(v); s8 = N["sens"]["s8"].get(v)
            rows.append([f"  {NB.LAB[v]}", f3(m), f"{100*mv['cred_frac']:.0f}" if mv else "Forced", f3(c4) if c4 else "–", f3(x) if x else "–", f3(s8) if s8 else "–"])
    foot = (f"CrI, credible interval; RR, rate ratio per 1 standard deviation; expected direction in parentheses. Principal model: negative binomial with a Besag–York–Mollié 2 district effect and random-walk and independent year effects, ten characteristics and five forced controls ({fmt(N['n_rows'])} district-years). "
            f"<sup>a</sup>Share of the {N['mv_total']} covariate-subset models containing the characteristic in which the CrI excluded 1. <sup>b</sup>Independent province-by-year effect added. <sup>c</sup>Refitted without 2020. <sup>d</sup>Crude expected recalls (no age-standardisation).")
    return (f"Table 2 District characteristics and breast screening recall, {N['n_districts']} districts, Republic of Korea, 2011–2024",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, %<sup>a</sup>", "Province-by-year RR (95% CrI)<sup>b</sup>", "Without 2020 RR (95% CrI)<sup>c</sup>", "Crude expected RR (95% CrI)<sup>d</sup>"], rows, foot)

FIGCAP = {
 1: "Flow of data. District screening counts were linked to female resident populations by district code, and national age-specific recall and screening rates were applied by age group and year to obtain expected counts; no district-year was excluded.",
 2: "Recall at national breast cancer screening, Republic of Korea, 2011–2024. <b>A</b> National recall per 100 women screened (line) and number screened (bars). <b>B</b> National recall per 100 women screened by 5-year age group in 2011, 2017 and 2024.",
 3: f"District geography of recall, {N['n_districts']} districts, Republic of Korea, 2011–2024. <b>A</b> Standardised recall ratio (observed over age-standardised expected recalls, 14 years pooled). <b>B</b> Residual spatial rate ratio from the principal model. <b>C</b> Residual hot spots and cold spots (posterior probability of a rate ratio above 1 greater than 0.95 or less than 0.05). Thick lines are province boundaries.",
 4: f"Recall and examinations judged suspicious for cancer, {N['n_districts']} districts, 2011–2024. <b>A</b> District standardised ratios (observed over age-standardised expected) of recall and of suspicious judgements (log scales; Seoul, Gyeonggi-do and Incheon, and other provinces shown in different colours). <b>B</b> Suspicious judgements per 1000 recalls by quarter of the district standardised recall ratio (bars, median; lines, interquartile range).",
 5: "Rate ratios per 1 standard deviation with 95% credible intervals for the ten district characteristics across models: principal model, independent province-by-year effect, refit without 2020, crude expected recalls, model adding care outside the district and hospital beds, and the best-fitting Knorr-Held space-time interaction model. The horizontal axis is on a log scale; expected directions in parentheses.",
}
def foot_row(J, text, sz=9, ls=13):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c

def all_keys(D):
    src = json.dumps(METHODS) + json.dumps(D, ensure_ascii=False)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})

AUTHOR_CONTRIB = "Seongdae Kim is the sole author and was responsible for conceptualisation, data curation, formal analysis, methodology, software, validation, visualisation, and writing of the original draft and its review and editing."
def declarations():
    return [("Ethical considerations", f"The Institutional Review Board of Hongik University approved this study (approval number {IRB}; continuing review {IRB2})."),
            ("Consent to participate", "The Institutional Review Board of Hongik University waived the requirement for informed consent because only published aggregate statistics without individual information were used."),
            ("Consent for publication", "Not applicable."),
            ("Declaration of conflicting interest", "The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."),
            ("Funding", "The author received no financial support for the research, authorship, and/or publication of this article."),
            ("Data availability", data_statement())]

def build(bw=0, aw=0):
    D = read_draft(); J = TX(cite="sup"); KEYS = all_keys(D)
    J.para(f"<b>{TITLE}</b>")
    J.head("Abstract", 1)
    for h, t in ABSTRACT: J.para(f"<b>{h}</b> {t}")
    J.para(f"<b>Keywords</b> {KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for x in METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for x in results():
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]: J.para(pandoc_cites(p), indent=True)
    J.head("Conclusions", 1)
    for p in D["Conclusions"]: J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Acknowledgements", 1); J.para(AI_STATEMENT)
    J.head("Author contributions", 1); J.para(AUTHOR_CONTRIB)
    J.head("Statements and Declarations", 1)
    for h, t in declarations(): J.head(h, 2); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); J.head("Figure legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}", after=6)
    J.page_break(); put_table(J, table1())
    J.new_page("landscape"); put_table(J, table2(), fs=8)
    return J, rl, D, KEYS

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    i = t.find("\nIntroduction\n"); j = t.find("\nAcknowledgements\n"); assert 0 < i < j; return len(t[i:j].split())
def intro_words(D): return sum(len(re.sub(r"\[@[^\]]+\]", "", p).split()) for p in D["Introduction"])

def title_page(bw, aw, nref):
    T = TX(cite="sup"); T.para(f"<b>{TITLE}</b>"); T.para("Seongdae Kim", before=12); T.para(AFFIL)
    T.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDRESS}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=12)
    T.para(f"<b>Word counts:</b> main text {bw} words; abstract {aw} words. <b>Tables:</b> 2. <b>Figures:</b> 5. <b>References:</b> {nref}. Supplementary material: one file (Appendix S1 and Tables S1–S5) and the STROBE checklist.", before=12)
    T.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    T.head("Acknowledgements", 1); T.para(AI_STATEMENT)
    T.head("Author contributions", 1); T.para(AUTHOR_CONTRIB)
    T.head("Statements and Declarations", 1)
    for h, t in declarations(): T.head(h, 2); T.para(t)
    T.doc_title = "Title page"; T.save(os.path.join(OUT, "Title_Page_JMS_BRRC.docx"))
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_brrc_tp", "--convert-to", "pdf", "--outdir", OUT, os.path.join(OUT, "Title_Page_JMS_BRRC.docx")], capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_JMS_BRRC.docx")
    aw = sum(len(t.split()) for _, t in ABSTRACT) + sum(len(h.split()) for h, _ in ABSTRACT)
    J, rl, D, KEYS = build(); J.save(p); bw = docx_bw(p)
    title_page(bw, aw, len(KEYS)); iw = intro_words(D)
    open(os.path.join(OUT, "wordcount_jms.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nintro_words={iw}\nrefs={len(KEYS)}\ntables=2\nfigures=5\ntitle_words={len(TITLE.split())}\nkeywords={len(KEYWORDS.split(';'))}\n")
    open(os.path.join(OUT, "reference_list.txt"), "w").write("\n".join(rl) + "\n")
    print(f"body {bw} | abstract {aw} | intro {iw} | refs {len(KEYS)}")
    assert bw <= 4000 and aw <= 250 and len(KEYWORDS.split(";")) >= 4
