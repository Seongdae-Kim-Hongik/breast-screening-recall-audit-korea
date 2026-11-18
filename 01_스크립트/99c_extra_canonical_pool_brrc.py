#!/usr/bin/env python3
# 99c — BRRC(유방암 검진 판정유보) 가설 풀용 추가 열(2026-11-13). 새 수집 없음.
#  공변량 ← EXT_canonical_pool_HCUV_261113(수급률 2021-23 양쪽 규칙 정정판: 수급률·고등교육·의원·종합병원·관외 진료 비중)
#  종속변수·연령 구성 ← 02_패널/BRRC_Eage.csv(50E: 판정유보 인원, 수검자, 40대 비율), 수검률 ← BRSU_Estd3r(유방암 검진 수검/대상), 80+ ← SKND_Esex
#  산출: 02_패널/EXT_canonical_pool_BRRC_261113.csv
import os, unicodedata, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); PAN = os.path.join(os.path.dirname(HERE), "02_패널")
def rd(f, cols):
    d = pd.read_csv(os.path.join(PAN, f), encoding="utf-8-sig"); d["fbd_region"] = d.fbd_region.map(NFC); return d[["year", "fbd_region"] + cols]
out = rd("EXT_canonical_pool_HCUV_261113.csv", ["basic_livelihood_rate", "tertiary_educated_share", "clinics_per_100k", "general_hospitals_per_100k", "outside_care_share", "beds_per_1000"])
e = rd("BRRC_Eage.csv", ["cases", "offset", "f4049_share", "f70p_share", "exam_4049_share_est"]).rename(columns={"cases": "brrc_recalls", "offset": "brst_examinees"})
u = rd("BRSU_Estd3r.csv", ["cases", "offset"]); u["breast_uptake"] = 100 * u.cases / u.offset; u = u[["year", "fbd_region", "breast_uptake"]]
s = rd("SKND_Esex.csv", ["pop80_share_raw"]).rename(columns={"pop80_share_raw": "pop80_share"})
for X in (e, u, s): out = out.merge(X, on=["year", "fbd_region"], how="left", validate="one_to_one")
r = out.fbd_region.map(out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
assert not (out.year.isin([2021, 2022, 2023]) & ((out.basic_livelihood_rate < 0.2 * r) | (out.basic_livelihood_rate > 5 * r))).any(), "수급률 정정 위반"
assert len(out) == 3206 and out.fbd_region.nunique() == 229 and out.notna().all().all(), out.isna().sum()
assert (out.groupby("year").fbd_region.nunique() == 229).all() and (out.fbd_region.str.startswith("세종").groupby(out.year).sum() == 1).all(), "세종·연도별 229 위반"
assert (out.brrc_recalls <= out.brst_examinees).all() and (out.brst_examinees > 0).all()
# 이웃 연도 붕괴·복사 점검(새 공변량): 이웃 평균 대비 20% 미만·5배 초과
for c in ("breast_uptake", "brst_examinees", "brrc_recalls", "clinics_per_100k", "f4049_share"):
    g = out.sort_values(["fbd_region", "year"]).groupby("fbd_region")[c]; nb = (g.shift(1) + g.shift(-1)) / 2
    bad = ((out.sort_values(["fbd_region", "year"])[c] < 0.2 * nb) | (out.sort_values(["fbd_region", "year"])[c] > 5 * nb)).sum()
    print(f"[99c-brrc] 이웃 연도 이상 칸 {c}: {int(bad)}")
nat = out.groupby("year").brrc_recalls.sum()
out.sort_values(["fbd_region", "year"]).to_csv(os.path.join(PAN, "EXT_canonical_pool_BRRC_261113.csv"), index=False, encoding="utf-8-sig")
print("[99c-brrc] 저장", out.shape, "판정유보 2011/2020/2024 =", int(nat[2011]), int(nat[2020]), int(nat[2024]), "결측 0·세종 14년·수급률 정정 위반 0")
