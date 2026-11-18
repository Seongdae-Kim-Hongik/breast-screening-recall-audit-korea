#!/usr/bin/env python3
# 50B — BRRC: 전국 연령별 유방암 검진 결과 판정 현황(KOSIS DT_35007_N018) 2011-24 수집(2026-11-13, 99R_next5d_fetch 복제·표만 교체).
#  키: ~/.kosis_key(내용 출력 금지). 산출: 00_원천/C_NHIS_검진보험/DT_35007_N018_national/<연도>.json, DT_35007_N018_national_long.csv
import os, json, time, urllib.request, urllib.parse
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); T = "DT_35007_N018"
KEY = open(os.path.expanduser("~/.kosis_key")).read().strip()
URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do?"
OUT = os.path.join(SRC, f"{T}_national"); os.makedirs(OUT, exist_ok=True); rows = []
for y in range(2011, 2025):
    f = os.path.join(OUT, f"{y}.json")
    if not os.path.exists(f):
        for nl in (3, 2, 1):
            q = dict(method="getList", apiKey=KEY, itmId="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y), orgId="350", tblId=T,
                     **{f"objL{i}": "ALL" for i in range(1, nl + 1)})
            d = json.loads(urllib.request.urlopen(URL + urllib.parse.urlencode(q), timeout=300).read().decode("utf-8"))
            if not (isinstance(d, dict) and d.get("err") == "21"): break
        assert isinstance(d, list), (y, d)
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False); time.sleep(1)
    for r in json.load(open(f, encoding="utf-8")):
        rows.append({k: r.get(k) for k in ("PRD_DE", "C1", "C1_NM", "C2", "C2_NM", "ITM_NM", "UNIT_NM", "DT")})
L = pd.DataFrame(rows); L.to_csv(os.path.join(SRC, f"{T}_national_long.csv"), index=False, encoding="utf-8-sig")
print("[50B]", L.shape, sorted(L.PRD_DE.unique()), L.C1_NM.unique().tolist(), L.C2_NM.unique().tolist())
