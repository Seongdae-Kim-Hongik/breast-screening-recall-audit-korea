#!/usr/bin/env python3
# 50F — BRRC: 유방암 검진 판정(N017) 시군구 집계를 (C1, C1_NM) 쌍으로 다시 결합(2026-11-14).
#  결함: 공용 99R_next5d_cancerscreen_E.py는 C1 하나로 결합하며 N009 대응을 우선 → N017의 부산 B112(연제구)·B113(강서구)이 N009(B112=강서구·B113=연제구)와 반대라 두 구 값이 뒤바뀜(14년×2곳). CXAB 세션 발견.
#  처리: 99R의 code_of(이름 기준)를 N017 자체 (C1, C1_NM)에 적용. 공유 원본은 수정하지 않는다.
#  산출: 02_패널/BRRC_counts_fix.csv (year, fbd_region, offset=수검, cases=판정유보, cases_sp=유방암 의심)
import os, sys, importlib.util, unicodedata, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
src = open(os.path.join(HERE, "99R_next5d_cancerscreen_E.py"), encoding="utf-8").read()
cut = src.index("frames = {T: load(T)"); g = {"__file__": os.path.join(HERE, "99R_next5d_cancerscreen_E.py"), "__name__": "x"}
exec(compile(src[:cut], "99R_head", "exec"), g)
L = g["load"]("DT_35007_N017"); L["sigungu_cd"] = [g["code_of"](a, b) for a, b in zip(L.C1, L.C1_NM)]
nat = L[L.C1 == "15350AC400Z1"]; d = L[L.sigungu_cd.notna()]
def agg(lab): return d[d.C2_NM == lab].groupby(["year", "sigungu_cd"]).DT.sum()
for lab in ("계", "판정유보", "유방암 의심"):
    r = agg(lab).groupby("year").sum() / nat[nat.C2_NM == lab].groupby("year").DT.sum(); assert ((r - 1).abs() < 0.002).all(), (lab, r)
base = g["base"][["year", "sigungu_cd", "fbd_region"]] if "base" in g else None
assert base is not None
X = base.set_index(["year", "sigungu_cd"]).join(agg("계").rename("offset")).join(agg("판정유보").rename("cases")).join(agg("유방암 의심").rename("cases_sp")).reset_index()
X["fbd_region"] = X.fbd_region.map(lambda s: unicodedata.normalize("NFC", s)); assert X[["offset", "cases", "cases_sp"]].notna().all().all() and len(X) == 3206
old = pd.read_csv(os.path.join(PAN, "BRRC_Estd3r.csv"), encoding="utf-8-sig"); old["fbd_region"] = old.fbd_region.map(lambda s: unicodedata.normalize("NFC", s))
m = X.merge(old[["year", "fbd_region", "offset", "cases"]], on=["year", "fbd_region"], suffixes=("", "_old")); diff = m[(m.offset != m.offset_old) | (m.cases != m.cases_old)]
print("[50F] 기존 BRRC_Estd3r 대비 바뀐 칸:", len(diff), sorted(diff.fbd_region.unique()))
assert set(diff.fbd_region) <= {"부산시연제구", "부산시강서구"}
X[["year", "fbd_region", "offset", "cases", "cases_sp"]].sort_values(["year", "fbd_region"]).to_csv(os.path.join(PAN, "BRRC_counts_fix.csv"), index=False, encoding="utf-8-sig")
print("[50F] 저장 02_패널/BRRC_counts_fix.csv", X.shape)
