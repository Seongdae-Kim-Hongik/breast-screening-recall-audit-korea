#!/usr/bin/env python3
# 50E — BRRC(유방암 검진 판정유보) 연령 간접표준화 E (2026-11-13).
#  시군구 판정 표(DT_35007_N017)에는 연령이 없다. 전국 표 두 개로 시군구 수검자의 연령 구성을 추정해 간접표준화한다.
#   ① 전국 연령별 판정유보율 r[y,a] = N018 판정유보/계 (40-44 … 80-84, 85+, 10구간)
#   ② 전국 연령별 수검 강도 u[y,a] = N010 유방암·여자 수검인원 / 전국 여자 인구[y,a] (격년 대상 포함, 인구 대비)
#   ③ 시군구 수검자 연령 가중 w[d,y,a] ∝ 여자 인구[d,y,a] × u[y,a] (Σ_a w = 1)
#   ④ E_agestd[d,y] = 수검자[d,y] × Σ_a w[d,y,a] r[y,a] → 연도별 ΣE = Σcases 재척도. E_crude = 수검자 × 전국 율(선별 단계 E)
#  시군구 수검·판정유보·의심 = 02_패널/BRRC_counts_fix.csv(50F).
#  여자 5세 인구: ST_FBDZIP(창원 2023 교정 인구) '여자' 열, 39m 매칭 규칙 그대로(일반구 → 시, 청원군 → 청주시, 세종 시도 머리행 포함).
#  산출: 02_패널/BRRC_Eage.csv (year, fbd_region, offset, cases, E_agestd, E_crude, f4049_share, f70p_share, exam_mean_age_est, uptake_brst)
#        02_패널/BRRC_national_agerates.csv
#  사용: ST_FBDZIP=<창원 교정 인구 폴더> python3 50E_brrc_Estd.py
import os, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
cw = _load("cw", "40_region_crosswalk.py"); FBDZIP = os.environ["ST_FBDZIP"]
NFC = lambda s: unicodedata.normalize("NFC", str(s))
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); PAN = os.path.join(ROOT, "02_패널")
B = ["40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"]
def band(a):
    a = str(a).replace(" ", "")
    if a.startswith("85"): return "85+"
    if a.endswith("세") and "~" in a: lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None

# ① 전국 연령별 판정유보율(N018)
N18 = pd.read_csv(os.path.join(SRC, "DT_35007_N018_national_long.csv"), encoding="utf-8-sig"); N18["band"] = N18.C1_NM.map(band); N18["DT"] = pd.to_numeric(N18.DT, errors="coerce")
rr = N18[N18.C2_NM == "판정유보"]; tt = N18[N18.C2_NM == "계"]
RC = rr[rr.band.notna()].pivot_table(index="PRD_DE", columns="band", values="DT", aggfunc="sum")[B]
EX = tt[tt.band.notna()].pivot_table(index="PRD_DE", columns="band", values="DT", aggfunc="sum")[B]
for X, src in ((RC, rr), (EX, tt)):
    tot = src[src.C1_NM == "계"].set_index("PRD_DE").DT
    assert ((X.sum(axis=1) - tot).abs() / tot < 0.002).all(), "N018 연령 합 ≠ 계"
R = RC / EX   # [year, band]
# ② 전국 유방암 수검(여자, 연령별, N010)
N10 = pd.read_csv(os.path.join(SRC, "DT_35007_N010_national_long.csv"), encoding="utf-8-sig")
N10 = N10[(N10.C3_NM == "유방암") & (N10.C2_NM == "여자") & (N10.ITM_NM == "수검인원")].copy(); N10["band"] = N10.C1_NM.map(band); N10["DT"] = pd.to_numeric(N10.DT, errors="coerce")
UX = N10[N10.band.notna()].pivot_table(index="PRD_DE", columns="band", values="DT", aggfunc="sum").reindex(columns=B)
assert UX.notna().all().all(), UX
assert ((UX - EX).abs() / EX).max().max() < 0.02, "N010 수검인원 ≠ N018 계(연령별)"

# ③ 시군구 여자 5세 인구(39m 매칭 규칙)
P = pd.read_csv(os.path.join(PAN, "BRRC_counts_fix.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)   # 50F: (C1, C1_NM) 결합 정정본(부산 연제구·강서구)
PK = pd.read_csv(os.path.join(ROOT, "04_분석", "BRRC", "panel_BRRC.csv"), encoding="utf-8-sig", usecols=["year", "key", "fbd_region", "population"])
PK["key"] = PK.key.map(NFC); PK["fbd_region"] = PK.fbd_region.map(NFC); PKEYS = set(PK.key)
SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(40, 85, 5)]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}; rows = []
for y in range(2011, 2025):
    d = pd.read_csv(os.path.join(FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip()
    d["vf"] = pd.to_numeric(d["여자"].str.replace(",", ""), errors="coerce"); d["vt"] = pd.to_numeric(d["전체"].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, g in d.groupby(blocks, sort=False):
        nm = g["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            g = g.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        a = g.set_index("연령별"); t = a.vt.get("계", np.nan); tf = a.vf.get("계", np.nan)
        if pd.isna(t): continue
        f = a.vf.reindex(FIVE); assert f.notna().all(), (y, nm)
        f85 = tf - a.vf.reindex([f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]).sum()
        r = {"year": y, "tot": t, "ftot": tf, **{b: f[b + "세"] for b in B[:-1]}, "85+": f85}
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        r["key"] = NFC(key); rows.append(r)
G = pd.DataFrame(rows).groupby(["year", "key"], as_index=False)[["tot", "ftot"] + B].sum()
X = PK.merge(G, on=["year", "key"], how="left", validate="one_to_one"); assert X.tot.notna().all(), X[X.tot.isna()][["year", "key"]]
assert ((X.tot / X.population - 1).abs() <= 0.01).all(), "총인구 비 1% 초과"
X = X.merge(P[["year", "fbd_region", "offset", "cases"]], on=["year", "fbd_region"], how="left", validate="one_to_one"); assert X.offset.notna().all() and (X.offset > 0).all()
assert len(X) == 3206 and X.fbd_region.nunique() == 229 and (X.groupby("year").fbd_region.nunique() == 229).all()
assert X[X.fbd_region.str.startswith("세종")].shape[0] == 14, "세종 14년 누락"

# ④ 가중·E
FP = X[B].values                                          # 시군구 여자 인구[d,a]
NATF = X.groupby("year")[B].sum()                         # 전국 여자 인구(시군구 합)
U = (UX / NATF).loc[X.year.values].values                 # 인구 대비 수검 강도
W = FP * U; W = W / W.sum(axis=1, keepdims=True)
Rm = R.loc[X.year.values].values
X["rate_exp"] = (W * Rm).sum(axis=1)
rs = lambda e: e * X.groupby("year").cases.transform("sum") / pd.Series(e, index=X.index).groupby(X.year).transform("sum")
X["E_agestd"] = rs((X.offset * X.rate_exp).values)
nat = X.groupby("year").cases.sum() / X.groupby("year").offset.sum(); X["E_crude"] = X.offset * X.year.map(nat)
for c in ("E_agestd", "E_crude"): assert (X.groupby("year")[c].sum() - X.groupby("year").cases.sum()).abs().max() < 1e-6 * X.cases.sum()
mid = np.array([42, 47, 52, 57, 62, 67, 72, 77, 82, 87.5])
X["exam_mean_age_est"] = (W * mid).sum(axis=1)
X["exam_4049_share_est"] = 100 * W[:, :2].sum(axis=1)
X["f4049_share"] = 100 * (X["40-44"] + X["45-49"]) / X[B].sum(axis=1)   # 40세 이상 여자 중 40대(치밀 유방 연령대) 비율
X["f70p_share"] = 100 * X[["70-74", "75-79", "80-84", "85+"]].sum(axis=1) / X[B].sum(axis=1)
X["uptake_brst"] = 100 * X.offset / (X[B].sum(axis=1) * 0.5)   # 40세 이상 여자의 절반(격년 대상) 대비 수검자 — 근사, 보조용
X["SIR_crude"] = X.cases / X.E_crude; X["SIR_agestd"] = X.cases / X.E_agestd
r_ = (X.E_agestd / X.E_crude)
print("[50E] E_agestd/E_crude:", r_.describe()[["min", "50%", "max"]].round(3).to_dict())
print("[50E] 수검자 평균 연령 추정:", X.exam_mean_age_est.describe()[["min", "50%", "max"]].round(2).to_dict())
from scipy.stats import spearmanr
g = X.groupby("fbd_region")[["cases", "E_agestd", "E_crude", "f4049_share", "f70p_share"]].sum(numeric_only=True)
g2 = X.groupby("fbd_region")[["f4049_share", "f70p_share"]].mean()
print("[50E] 14년 SIR ρ(crude vs agestd):", round(spearmanr(g.cases / g.E_crude, g.cases / g.E_agestd)[0], 3),
      "| SIR_crude–40대 비율 ρ:", round(spearmanr(g.cases / g.E_crude, g2.f4049_share)[0], 3), "| SIR_agestd–40대 비율 ρ:", round(spearmanr(g.cases / g.E_agestd, g2.f4049_share)[0], 3),
      "| SIR_agestd–70+ ρ:", round(spearmanr(g.cases / g.E_agestd, g2.f70p_share)[0], 3))
cols = ["year", "fbd_region", "offset", "cases", "E_agestd", "E_crude", "SIR_crude", "SIR_agestd", "exam_mean_age_est", "exam_4049_share_est", "f4049_share", "f70p_share", "uptake_brst"]
X[cols].sort_values(["year", "fbd_region"]).to_csv(os.path.join(PAN, "BRRC_Eage.csv"), index=False, encoding="utf-8-sig")
RT = R.stack().rename("rate").reset_index().rename(columns={"PRD_DE": "year"}); RT["recalls"] = RC.stack().values; RT["examinees"] = EX.stack().values
RT.to_csv(os.path.join(PAN, "BRRC_national_agerates.csv"), index=False, encoding="utf-8-sig")
print("[50E] 저장 02_패널/BRRC_Eage.csv", X[cols].shape, "· BRRC_national_agerates.csv")
print("[50E] 전국 판정유보율(%) 2011/2020/2024:", (100 * X.groupby("year").cases.sum() / X.groupby("year").offset.sum()).loc[[2011, 2020, 2024]].round(2).to_dict())

# ── 보조(50D용): 같은 연령 가중으로 '유방암 의심' 판정 E(BRSP) — 판정유보 대비 의심 비(양성예측 대리) 기술 ──
sp = N18[N18.C2_NM == "유방암의심"]; SPC = sp[sp.band.notna()].pivot_table(index="PRD_DE", columns="band", values="DT", aggfunc="sum")[B]; RSP = SPC / EX
BS = P[["year", "fbd_region", "cases_sp"]]
X = X.merge(BS, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert X.cases_sp.notna().all()
e_sp = X.offset * (W * RSP.loc[X.year.values].values).sum(axis=1); X["E_sp_agestd"] = e_sp * X.groupby("year").cases_sp.transform("sum") / e_sp.groupby(X.year).transform("sum")
X[["year", "fbd_region", "offset", "cases", "E_agestd", "cases_sp", "E_sp_agestd"]].to_csv(os.path.join(PAN, "BRRC_Eage_aux.csv"), index=False, encoding="utf-8-sig")
print("[50E] 보조 저장 02_패널/BRRC_Eage_aux.csv (유방암 의심 E 포함)")
