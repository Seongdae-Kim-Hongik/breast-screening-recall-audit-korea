# gate_judgement_brrc.py — national judgement composition of breast cancer screening by year (four categories + existing cancer) from the district judgement table (KOSIS DT_35007_N017),
#  checked against the programme recall rate (BI-RADS 0, 3, 4, 5) published by Kim DJ et al., Korean J Radiol 2025;26:313, Table 2 (2011–2020). Output: out_jms/S5_judgement_composition.csv (Supplementary Table S1).
import json, glob, os, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out_jms")
SRC = os.path.join(os.environ.get("ST_ROOT", os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))), "00_원천", "C_NHIS_검진보험", "DT_35007_N017_sgg")
SIDO = {"서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"}
KJR = {2011: 14.56, 2012: 14.66, 2013: 14.53, 2014: 14.91, 2015: 14.61, 2016: 14.17, 2017: 13.99, 2018: 13.02, 2019: 11.92, 2020: 11.17}   # Kim DJ et al. Korean J Radiol 2025;26:313, Table 2 RR %
rows = []
for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    d = pd.DataFrame(json.load(open(f))); y = int(d.PRD_DE.iloc[0]); d["DT"] = pd.to_numeric(d.DT, errors="coerce")
    nat = d[d.C1_NM.isin({"전국", "계"})]
    if len(nat) == 0:
        top = d[d.C1_NM.isin(SIDO)]; top = top[top.C1.str.len() == top.C1.str.len().min()]   # 시도 머리행
        g = top.groupby("C2_NM").DT.sum()
    else: g = nat.groupby("C2_NM").DT.sum()
    t = g["계"]; four = g[["이상소견 없음", "양성질환", "판정유보", "유방암 의심"]].sum(); assert abs(t - four) / t < 1e-4, (y, t, four)   # 4범주 합 = 계, 기존 암환자는 계 밖 별도 행
    rows.append(dict(year=y, screened=int(t), normal=100 * g["이상소견 없음"] / t, benign=100 * g["양성질환"] / t, recall=100 * g["판정유보"] / t, suspicious=100 * g["유방암 의심"] / t, existing=100 * g["기존 암환자"] / t))
D = pd.DataFrame(rows).set_index("year"); D["recall_plus_susp"] = D.recall + D.suspicious; D["KJR_RR"] = pd.Series(KJR); D["diff_pp"] = D.recall_plus_susp - D.KJR_RR
D.round(3).to_csv(os.path.join(OUT, "S5_judgement_composition.csv"), encoding="utf-8-sig")
print(D.round(2).to_string()); print("max |diff| pp", D.diff_pp.abs().max().round(3))
