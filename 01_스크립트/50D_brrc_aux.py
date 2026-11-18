#!/usr/bin/env python3
# 50D — BRRC 보조 기술 분석(2026-11-13). 모형 아님, 시군구 14년 통합 SIR 비교.
#  ① 판정유보 SIR vs 같은 수검자의 '유방암 의심' SIR(연령 가중 동일) → 판정유보 대비 의심 비(양성예측 대리)의 지리
#  ② 판정유보 SIR vs 자궁경부 세포 이상(CXAB, 같은 검진 프로그램·다른 검사) vs 유방암 진료(BRCA, 2호) — 순위 상관
#  ③ 2020(코로나19): 전국 수검·판정유보 변화, 시군구 SIR 2019·2020·2021 순위 상관, 수검 감소율과 SIR 변화 상관
#  ④ 시도 간·시도 안 분산 비(로그 SIR, 14년 통합과 연도별 평균) — 검진 기관·판독 관행의 지역 군집 기술
#  산출: 04_분석/BRRC/results_std3/S50D_aux_*.csv, S50D_aux_summary.json
import os, json, unicodedata
import numpy as np, pandas as pd
from scipy.stats import spearmanr
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
OUT = os.path.join(ROOT, "04_분석", "BRRC", "results_std3"); os.makedirs(OUT, exist_ok=True)
rd = lambda f: (lambda d: d.assign(fbd_region=d.fbd_region.map(NFC)))(pd.read_csv(os.path.join(PAN, f), encoding="utf-8-sig"))
A = rd("BRRC_Eage_aux.csv"); P = pd.read_csv(os.path.join(ROOT, "04_분석", "BRRC", "panel_BRRC_std3.csv"), encoding="utf-8-sig", usecols=["year", "fbd_region", "sido_std"]); P["fbd_region"] = P.fbd_region.map(NFC)
A = A.merge(P, on=["year", "fbd_region"], validate="one_to_one")
S = {}
g = A.groupby("fbd_region").agg(cases=("cases", "sum"), E=("E_agestd", "sum"), sp=("cases_sp", "sum"), Esp=("E_sp_agestd", "sum"), sido=("sido_std", "first"))
g["SIR"] = g.cases / g.E; g["SIR_sp"] = g.sp / g.Esp; g["sp_per_1000_recalls"] = 1000 * g.sp / g.cases
S["recall_vs_suspicion_rho"] = round(spearmanr(g.SIR, g.SIR_sp)[0], 3)
S["recall_vs_ppvproxy_rho"] = round(spearmanr(g.SIR, g.sp_per_1000_recalls)[0], 3)
S["ppvproxy_median_IQR"] = [round(float(x), 2) for x in g.sp_per_1000_recalls.quantile([.5, .25, .75])]
S["SIR_P10_P90"] = [round(float(x), 3) for x in g.SIR.quantile([.1, .9])]
S["SIR_sp_P10_P90"] = [round(float(x), 3) for x in g.SIR_sp.quantile([.1, .9])]
# 사분위 교차: 판정유보 상위 사분위 시군구의 의심 SIR 중앙
q = pd.qcut(g.SIR, 4, labels=["Q1", "Q2", "Q3", "Q4"]); S["SIR_sp_median_by_recall_quartile"] = g.groupby(q, observed=True).SIR_sp.median().round(3).to_dict()
S["ppvproxy_median_by_recall_quartile"] = g.groupby(q, observed=True).sp_per_1000_recalls.median().round(2).to_dict()
# ② CXAB·BRCA
def sir14(tag, efile, ecol):
    c = pd.read_csv(os.path.join(ROOT, "04_분석", tag, f"panel_{tag}.csv"), encoding="utf-8-sig", usecols=["year", "fbd_region", "cases"]); c["fbd_region"] = c.fbd_region.map(NFC)
    e = rd(efile)[["year", "fbd_region", ecol]]; m = c.merge(e, on=["year", "fbd_region"]); h = m.groupby("fbd_region")[["cases", ecol]].sum(); return h.cases / h[ecol]
cx = rd("CXAB_Estd3r.csv"); _a, _b = cx.fbd_region == "부산시연제구", cx.fbd_region == "부산시강서구"; cx.loc[_a, "fbd_region"], cx.loc[_b, "fbd_region"] = "부산시강서구", "부산시연제구"   # 공용 99R의 C1 단독 결합으로 N019 연제·강서가 뒤바뀐 것을 되돌림; E_std = 수검자×전국율이라 함께 이동
cxs = cx.groupby("fbd_region").cases.sum() / cx.groupby("fbd_region").E_std.sum()
br = sir14("BRCA", "BRCA_Estd.csv", "E_std")
S["recall_vs_CXAB_rho"] = round(spearmanr(g.SIR, cxs.reindex(g.index))[0], 3)
S["recall_vs_BRCA_treated_rho"] = round(spearmanr(g.SIR, br.reindex(g.index), nan_policy="omit")[0], 3)
S["suspicion_vs_BRCA_treated_rho"] = round(spearmanr(g.SIR_sp, br.reindex(g.index), nan_policy="omit")[0], 3)
g.assign(SIR_CXAB=cxs.reindex(g.index), SIR_BRCA=br.reindex(g.index)).to_csv(os.path.join(OUT, "S50D_aux_district.csv"), encoding="utf-8-sig")
# ③ 2020
nat = A.groupby("year").agg(exam=("offset", "sum"), rec=("cases", "sum")); nat["rate_pct"] = 100 * nat.rec / nat.exam
S["national_examinees_2019_2020_2021"] = nat.loc[[2019, 2020, 2021], "exam"].astype(int).tolist()
S["national_recall_pct_2019_2020_2021"] = nat.loc[[2019, 2020, 2021], "rate_pct"].round(2).tolist()
A["SIR"] = A.cases / A.E_agestd; W = A.pivot(index="fbd_region", columns="year", values="SIR"); X = A.pivot(index="fbd_region", columns="year", values="offset")
S["SIR_rank_rho_2019_2020"] = round(spearmanr(W[2019], W[2020])[0], 3); S["SIR_rank_rho_2020_2021"] = round(spearmanr(W[2020], W[2021])[0], 3); S["SIR_rank_rho_2019_2021"] = round(spearmanr(W[2019], W[2021])[0], 3)
adj = [round(spearmanr(W[y], W[y + 1])[0], 3) for y in range(2011, 2024)]; S["SIR_rank_rho_adjacent_years"] = dict(zip([f"{y}-{y+1}" for y in range(2011, 2024)], adj))
drop = X[2020] / X[2019] - 1; dS = np.log(W[2020] / W[2019]); S["exam_drop_vs_logSIR_change_2020_rho"] = round(spearmanr(drop, dS)[0], 3)
S["exam_drop_2020_median_P10_P90_pct"] = [round(100 * float(x), 1) for x in drop.quantile([.5, .1, .9])]
pd.DataFrame(nat).to_csv(os.path.join(OUT, "S50D_aux_national_year.csv"), encoding="utf-8-sig")
# ④ 시도 간·안 분산
def bw(v, grp):
    tot = v.var(ddof=0); btw = v.groupby(grp).transform("mean").var(ddof=0); return round(float(btw / tot), 3)
ls = np.log(g.SIR); S["between_province_share_logSIR_pooled"] = bw(ls, g.sido)
yr = [bw(np.log(A[A.year == y].SIR), A[A.year == y].sido_std.values) for y in range(2011, 2025)]
S["between_province_share_logSIR_yearly_mean_min_max"] = [round(float(np.mean(yr)), 3), min(yr), max(yr)]
gs = g.assign(ls=ls).groupby("sido").ls.agg(["mean", "std", "count"]).round(3); gs.to_csv(os.path.join(OUT, "S50D_aux_province.csv"), encoding="utf-8-sig")
json.dump(S, open(os.path.join(OUT, "S50D_aux_summary.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
