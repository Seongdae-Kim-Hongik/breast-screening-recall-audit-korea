# numbers_brrc.py — BRRC European Radiology 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-13, numbers_sknd 구조 이식). 손입력 금지, assert로 정합 확인.
import os, glob, json, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널")
SHP = os.environ.get("ST_SHP", os.path.expandvars("$ST_DATA_ROOT") + "/기타/R_Studio/FBD_DATA_ZIP/final.shp")
WIN = [("W1_2011-15", 2011, 2015), ("W2_2016-19", 2016, 2019), ("W3_2020-24", 2020, 2024)]
rd = lambda f, d=RS, **k: pd.read_csv(os.path.join(d, f), encoding="utf-8-sig", **k)
F40, OB, TE, UP, CL, GH, BL = ("ext__f4049_share", "screening_normalB_obesity_share", "tertiary_educated_share", "ext__breast_uptake", "ext__clinics_per_100k", "ext__general_hospitals_per_100k", "basic_livelihood_rate")
WK, MP, FAC = "walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k"
HYP = [F40, OB, TE, UP, CL, GH, BL, WK, MP, FAC]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
LAB = {F40: "Women aged 40–49 years (+)", OB: "Obesity at health screening (−)", TE: "Tertiary-educated adults (+)", UP: "Breast screening uptake (−)",
       CL: "Clinics per 100 000 (+)", GH: "General hospitals per 100 000 (−)", BL: "Basic livelihood recipients (+)", WK: "Walking (−)", MP: "Moderate-to-vigorous physical activity (−)", FAC: "Public sports facilities per 100 000 (−)",
       "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥ 80 years"}
t4 = lambda r: (r.IRR, r.lo, r.hi, bool(r.cred))

def load():
    N = {"HYP": HYP, "LAB": LAB}
    P = pd.read_csv(os.path.join(B, "panel_BRRC_std3.csv")); N["n_rows"], N["n_districts"] = len(P), P.fbd_region.nunique(); assert (N["n_rows"], N["n_districts"]) == (3206, 229)
    N["P"] = P
    A = pd.read_csv(os.path.join(PAN, "BRRC_Eage_aux.csv"), encoding="utf-8-sig"); N["exam_total"] = int(A.offset.sum()); N["cases_total"] = int(A.cases.sum()); N["sp_total"] = int(A.cases_sp.sum())
    assert N["cases_total"] == int(P.cases.sum()) == 6959608 and abs(P.offset.sum() - N["exam_total"]) < 1
    E = pd.read_csv(os.path.join(PAN, "BRRC_Eage.csv"), encoding="utf-8-sig"); N["E_ratio"] = (E.E_agestd / E.E_crude).quantile([0, .5, 1]).round(2).tolist()
    N["exam_age"] = E.exam_mean_age_est.quantile([0, .5, 1]).round(1).tolist()
    g14 = E.groupby("fbd_region")[["cases", "E_agestd", "E_crude"]].sum(); N["rho_crude_std"] = float(spearmanr(g14.cases / g14.E_crude, g14.cases / g14.E_agestd)[0])
    f40 = E.groupby("fbd_region").f4049_share.mean(); N["rho_f40_crude"] = float(spearmanr(g14.cases / g14.E_crude, f40.reindex(g14.index))[0]); N["rho_f40_std"] = float(spearmanr(g14.cases / g14.E_agestd, f40.reindex(g14.index))[0])
    RT = pd.read_csv(os.path.join(PAN, "BRRC_national_agerates.csv")); N["agerate"] = {(r.year, r.band): r.rate for r in RT.itertuples()}
    AX = json.load(open(os.path.join(RS, "S50D_aux_summary.json"))); N["aux"] = AX
    D = rd("S50D_aux_district.csv").set_index("fbd_region"); N["district"] = D
    q = pd.qcut(D.SIR, 4, labels=["Q1", "Q2", "Q3", "Q4"]); N["ppv_q"] = {k: dict(median=float(v.median()), p25=float(v.quantile(.25)), p75=float(v.quantile(.75))) for k, v in D.sp_per_1000_recalls.groupby(q, observed=True)}
    NY = rd("S50D_aux_national_year.csv").set_index("year"); N["nat_year"] = NY
    T1 = {}
    for wn, a, b in WIN + [("ALL", 2011, 2024)]:
        qd = P[P.year.between(a, b)]; sir = qd.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(qd), exam=int(qd.offset.sum()), cases=int(qd.cases.sum()), rate=100 * qd.cases.sum() / qd.offset.sum(), p10=sir.quantile(.1), med=sir.median(), p90=sir.quantile(.9),
                      cov={v: (qd[f"{v}_raw"].mean(), qd[f"{v}_raw"].std()) for v in HYP + FORCED})
    N["T1"] = T1
    L = rd("S50K_likelihood.csv").set_index("likelihood"); N["lik"] = L.to_dict("index")
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = lk["poisson"], lk["nbinomial"]; assert N["waic_nb"] < N["waic_pois"]
    hb = open(os.path.join(B, "HM_best_BRRC_std3.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0]); N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    s6m = rd("S6_moran_year.csv"); N["moran_year"] = (s6m.moran_I.min(), s6m.moran_I.max())
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]; N["moran_resid"], N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "moran_I"], r8.loc["pearson_residual_area_mean", "p_perm"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["s6"] = s6; N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum())
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict(); N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = {v: t4(r) for v, r in m3.iterrows()}; assert set(m3.index[m3.role == "hypothesis"]) == set(HYP)
    N["cred_hyp"] = [v for v in HYP if N["main"][v][3]]
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index"); N["mv_total"] = int(s7.n_specs_total.iloc[0]); N["robust"] = list(s7.index[s7.robust])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = {v: t4(r) for v, r in nc.iterrows()}
    wi = rd("S4_window_IRR.csv"); N["win"] = {(r.cov, r.window): t4(r) for r in wi.itertuples()}
    cv = rd("S5_covid.csv"); N["covid_main"] = tuple(cv[cv.term == "post_main"][["IRR", "lo", "hi", "cred"]].iloc[0]); N["covid_inter"] = {r.cov: t4(r) for r in cv[cv.term == "var_x_post"].itertuples()}
    _f43 = glob.glob(os.path.join(RS, "S43_part_*.csv")); S43 = pd.concat([pd.read_csv(f) for f in _f43]) if _f43 else pd.DataFrame(columns=["analysis", "cov", "IRR", "lo", "hi", "cred", "WAIC"]); N["s43"] = {(r.analysis, r.cov): t4(r) for r in S43.itertuples()}; N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    if os.path.exists(os.path.join(RS, "S9_typeI_IRR.csv")):
        T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): t4(r) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    KH = [k for k in ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV") if k in N["s43_waic"]]; N["KH"] = KH; N["BEST_KH"] = min(KH, key=lambda a: N["s43_waic"][a]) if KH else None
    _f41 = glob.glob(os.path.join(RS, "S41_part_*.csv")); S41 = pd.concat([pd.read_csv(f) for f in _f41]) if _f41 else pd.DataFrame(columns=["analysis", "cov", "IRR", "lo", "hi", "cred", "WAIC"]); N["s41"] = {(r.analysis, r.cov): t4(r) for r in S41.itertuples()}; N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict()
    N["alt"] = sorted({a for a in S41.analysis.unique() if not a.startswith(("F1_", "F2_", "G2_", "H1_", "bw_"))})
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): t4(r) for r in S41[S41.analysis.str.startswith("H1_nco_")].itertuples()}
    N["bw"] = {r.cov: t4(r) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["n_alt_cred"] = {v: sum(1 for a in N["alt"] if N["s41"].get((a, v), (0, 0, 0, False))[3]) for v in HYP}
    N["n_drop_cred"] = {v: (sum(1 for (a, c), t in N["s41"].items() if c == v and a.startswith(("F1_", "F2_")) and t[3]), sum(1 for (a, c) in N["s41"] if c == v and a.startswith(("F1_", "F2_")))) for v in HYP}
    N["sens"] = {}
    for v in ("s577", "s2", "s8", "sx20", "si"):
        f = os.path.join(B, f"results_{v}", "S3_main_IRR.csv")
        if os.path.exists(f): m = pd.read_csv(f).set_index("cov"); N["sens"][v] = {c: t4(r) for c, r in m.iterrows()}
        else: N["sens"][v] = {}
    vp = os.path.join(RS, "S42_variance_partition.csv")
    if os.path.exists(vp): vp = rd("S42_variance_partition.csv").set_index("component"); N["vp"] = vp.share_of_linear_predictor_var.to_dict()
    pe = os.path.join(RS, "S12_persistence.csv")
    if os.path.exists(pe): N["kendall"] = rd("S12_persistence.csv").set_index("set").kendall_W.to_dict()
    w = P.groupby(["fbd_region", "window"]).agg(c=("cases", "sum"), e=("E", "sum")).reset_index(); w["sir"] = w.c / w.e
    pw = w.pivot(index="fbd_region", columns="window", values="sir").corr(method="spearman"); N["rho_win"] = (pw.values[np.triu_indices(3, 1)].min(), pw.values[np.triu_indices(3, 1)].max())
    g = P.groupby("fbd_region").agg(c=("cases", "sum"), e=("E", "sum"), fac=(f"{FAC}_raw", "mean"), pop=("population", "mean"), urb=("urban_population_share_raw", "mean")); g["srr"] = g.c / g.e
    N["fac_rho"] = {k: float(spearmanr(g.fac, g[k])[0]) for k in ("srr", "pop", "urb")}
    N["fac_year"] = P.groupby("year")[f"{FAC}_raw"].mean().to_dict()
    return N

if __name__ == "__main__":
    N = load()
    for k, v in N.items():
        if isinstance(v, (int, float, str, tuple)) or k in ("cred_hyp", "robust", "E_ratio", "exam_age", "KH", "hot_by_sido", "cold_by_sido", "n_alt_cred", "n_drop_cred", "kendall", "vp", "ppv_q"): print(k, v)
    for v in HYP: print(v, N["main"][v], N["mv"][v], {s: N["sens"][s].get(v) for s in N["sens"]}, N["s41"].get(("C4_sido_year_iid", v)), N["s41"].get(("F2_drop_year_2020", v)))
