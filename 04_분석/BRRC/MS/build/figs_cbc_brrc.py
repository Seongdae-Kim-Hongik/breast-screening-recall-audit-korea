# -*- coding: utf-8 -*-
# figs_cbc_brrc.py (재투고판 11/18: 패널 대문자 A,B,C, 출력 out_cbc, 파일 Figure_1.tif)
#  방위표 3배, 그림 안 설명문 없음, 시군구 결합은 코드로만. TIFF: 지도·그래프 600 dpi, 순서도 1200 dpi.
#  Fig 1 순서도 · Fig 2 (a) 전국 판정유보율 (b) 연령별 판정유보율 2011·2017·2024 · Fig 3 지도 (a) 연령표준화 SIR (b) 잔차 공간 RR (c) 핫·콜드스팟
#  Fig 4 (a) 판정유보 SIR 대 유방암 의심 SIR (b) 판정유보 사분위별 판정유보 1,000건당 의심 · Fig 5 주요 변수 모형별 RR
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_brrc import load, SHP, PAN, RS, B
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs_cbc"); OUTF = os.path.join(os.path.dirname(HERE), "out_cbc", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 170 * MM; DPI = 600; LW = 0.3
PANEL_LABEL_PT = 54
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "legend.fontsize": 8, "legend.title_fontsize": 8.5, "axes.linewidth": 0.6, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["region"] = G.region.map(NFC); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
assert G.region.is_unique and len(G) == 229
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def label(fig, ax, ch, dx=-0.02, dy=0.01):
    bb = ax.get_position(); fig.text(bb.x0 + dx, bb.y1 + dy, ch, fontsize=PANEL_LABEL_PT, fontweight="bold", va="bottom", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#303030", linewidth=0.5); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by, bh = x0 + 0.55 * W_, y0 + 0.03 * H_, 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + k, by + bh + 0.01 * H_, t, ha="center", va="bottom", fontsize=6.5)
    ax.text(bx + 100000 + 0.015 * W_, by + bh / 2, "km", ha="left", va="center", fontsize=6.5)
    nx, ny, nw, nh = x0 + 0.93 * W_, y0 + 0.40 * H_, 0.06 * W_, 0.20 * H_
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=22, fontweight="bold")
def save(fig, k, dpi=DPI):
    p = os.path.join(FIG, f"Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure_{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size
fmt = lambda x: f"{x:,}".replace(",", " ")

# Fig 1 순서도
fig = plt.figure(figsize=(W, 4.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_axis_off()
def box(x, y, w, h, t, fs=7.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc="white", ec="black", lw=0.7)); ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.35)
def arr(x0, y0, x1, y1): ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", lw=0.8, color="black", mutation_scale=9))
box(2, 72, 30, 22, f"District screening tables\n(women screened and judgements,\n{N['n_districts']} districts, 2011–2024)")
box(35, 72, 30, 22, "National age-specific tables\n(judgements and screening by\n5-year age group, 40 to ≥ 85 years)")
box(68, 72, 30, 22, "Resident registration\n(women by district and\n5-year age group)")
box(18, 40, 64, 20, f"Linkage by administrative district code\n{N['n_rows']:,} district-years ({N['n_districts']} districts × 14 years); no exclusions, no missing cells\n{fmt(N['exam_total'])} screening examinations".replace(",", " ", 1) if False else
    f"Linkage by administrative district code\n{fmt(N['n_rows'])} district-years ({N['n_districts']} districts × 14 years); no exclusions, no missing cells\n{fmt(N['exam_total'])} screening examinations")
box(2, 6, 45, 22, f"Recall ('judgement deferred')\n{fmt(N['cases_total'])} examinations\nAge-standardised expected recalls")
box(53, 6, 45, 22, f"Judged suspicious for cancer\n{fmt(N['sp_total'])} examinations\nSame age weights")
for x in (17, 50, 83): arr(x, 72, 50 if x == 50 else (30 if x < 50 else 70), 60.6)
arr(35, 40, 24.5, 28.6); arr(65, 40, 75.5, 28.6)
s1 = save(fig, 1, dpi=1200)

# Fig 2 전국 추이·연령
NY = N["nat_year"]; RT = pd.read_csv(os.path.join(PAN, "BRRC_national_agerates.csv")); yrs = list(range(2011, 2025))
fig = plt.figure(figsize=(W, 4.4)); a1 = fig.add_axes([0.10, 0.24, 0.36, 0.52]); a2 = fig.add_axes([0.61, 0.24, 0.36, 0.52])
a1b = a1.twinx(); a1b.bar(yrs, NY.loc[yrs, "exam"] / 1e6, color="#D1E5F0", width=0.75, zorder=0, label="Women screened (millions)")
a1.set_zorder(a1b.get_zorder() + 1); a1.patch.set_visible(False)
a1.plot(yrs, NY.loc[yrs, "rate_pct"], color="#B2182B", marker="o", ms=3, lw=1.1, label="Recall, %")
assert NY.rate_pct.max() < 16 and NY.exam.max() / 1e6 < 5; a1.set_ylim(0, 16); a1b.set_ylim(0, 5); a1.set_ylabel("Recall per 100 women screened"); a1b.set_ylabel("Women screened (millions)")
a1.set_xticks([2011, 2015, 2020, 2024])
h = [Line2D([0], [0], color="#B2182B", marker="o", ms=3, lw=1.1, label="Recall"), Patch(facecolor="#D1E5F0", label="Women screened")]
a1.legend(handles=h, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=7.5)
BANDS = ["40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"]; xl = [b.replace("-", "–").replace("85+", "≥ 85") for b in BANDS]
for y, c, mk in ((2011, "#2166AC", "s"), (2017, "#8073AC", "D"), (2024, "#B2182B", "o")):
    v = RT[RT.year == y].set_index("band").rate.reindex(BANDS) * 100; a2.plot(range(10), v, color=c, marker=mk, ms=3, lw=1.0, label=str(y))
assert RT.rate.max() * 100 < 24; a2.set_ylim(0, 24); a2.set_xticks(range(10)); a2.set_xticklabels(xl, rotation=45, ha="right", fontsize=7); a2.set_xlabel("Age group, years", labelpad=1)
a2.set_ylabel("Recall per 100 women screened"); a2.legend(frameon=False, loc="upper right", fontsize=7.5)
for a in (a1, a2, a1b): a.spines[["top"]].set_visible(False); a.tick_params(labelsize=8)
a2.spines[["right"]].set_visible(False)
label(fig, a1, "A", dx=-0.085, dy=0.02); label(fig, a2, "B", dx=-0.085, dy=0.02)
s2 = save(fig, 2)

# Fig 3 지도
S6 = N["s6"].copy(); S6["cd"] = S6.sigungu_cd.astype(str); assert S6.cd.nunique() == 229 and set(S6.cd) == set(G.cd)
d = S6.set_index("cd"); R2C = dict(zip(G.region, G.cd))
sm = N["district"].copy(); sm.index = sm.index.map(NFC).map(R2C); assert sm.index.notna().all() and sm.index.nunique() == 229
d["SIR"] = sm.SIR.reindex(d.index)
BR = [0, 0.67, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 99]; LB = ["< 0.67", "0.67–0.79", "0.80–0.89", "0.90–0.99", "1.00–1.09", "1.10–1.24", "1.25–1.49", "≥ 1.50"]
PAL = ["#053061", "#2166AC", "#67A9CF", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
for c in ("SIR", "RR"): assert d[c].min() >= BR[0] and d[c].max() < BR[-1]
fig = plt.figure(figsize=(W, 4.6)); pos = [[0.00, 0.20, 0.33, 0.70], [0.335, 0.20, 0.33, 0.70], [0.67, 0.20, 0.33, 0.70]]
for (col, ch), p in zip((("SIR", "A"), ("RR", "B")), pos[:2]):
    ax = fig.add_axes(p); gg = G.copy(); gg["v"] = gg.cd.map(d[col]); assert gg.v.notna().all()
    gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, ch, dx=0.0, dy=-0.005)
fig.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)], title="Ratio (A, observed/expected; B, residual spatial)", loc="upper center", bbox_to_anchor=(0.335, 0.20), ncol=4, frameon=False, columnspacing=0.9, handlelength=1.2, fontsize=7)
ax = fig.add_axes(pos[2]); gg = G.copy(); gg["k"] = gg.cd.map(d["class"]); assert gg.k.notna().all()
CK = {"hotspot": "#B2182B", "coldspot": "#2166AC", "neutral": "#EFEFEF"}; gg.plot(ax=ax, color=gg.k.map(CK), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, "C", dx=0.0, dy=-0.005)
fig.legend(handles=[Patch(facecolor=CK[k], edgecolor="#777777", linewidth=LW, label=l) for k, l in (("hotspot", f"Hot spot ({N['n_hot']})"), ("coldspot", f"Cold spot ({N['n_cold']})"), ("neutral", "Neither"))],
           loc="upper center", bbox_to_anchor=(0.835, 0.20), ncol=1, frameon=False, fontsize=7.5, handlelength=1.2)
s3 = save(fig, 3)

# Fig 4 판정유보 대 의심
g = N["district"]; fig = plt.figure(figsize=(W, 4.6)); a1 = fig.add_axes([0.13, 0.27, 0.34, 0.52]); a2 = fig.add_axes([0.63, 0.27, 0.34, 0.52])
REG = {"Seoul": "#B2182B", "Gyeonggi-do and Incheon": "#F4A582", "Other provinces": "#2166AC"}
grp = g.sido.map(lambda s: "Seoul" if s == "서울시" else ("Gyeonggi-do and Incheon" if s in ("경기도", "인천시") else "Other provinces"))
for k, c in REG.items():
    m = grp == k; a1.scatter(g.SIR[m], g.SIR_sp[m], s=9, color=c, alpha=0.85, lw=0, label=k)
assert g.SIR.max() < 2.2 and g.SIR_sp.max() < 3.2 and g.SIR.min() > 0.3 and g.SIR_sp.min() > 0.2
a1.set_xscale("log"); a1.set_yscale("log"); a1.set_xlim(0.3, 2.2); a1.set_ylim(0.2, 3.2)
for a_, t in ((a1.xaxis, [0.4, 0.6, 1, 1.5, 2]), (a1.yaxis, [0.25, 0.5, 1, 2, 3])): a_.set_ticks(t); a_.set_ticklabels([f"{x:g}" for x in t]); a_.set_minor_locator(matplotlib.ticker.NullLocator())
a1.axvline(1, color="#909090", lw=0.5); a1.axhline(1, color="#909090", lw=0.5)
a1.set_xlabel("Recall, observed/expected"); a1.set_ylabel("Judged suspicious for cancer,\nobserved/expected"); a1.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, handletextpad=0.2, columnspacing=0.8)
Q = N["ppv_q"]; xq = np.arange(4)
a2.bar(xq, [Q[k]["median"] for k in ("Q1", "Q2", "Q3", "Q4")], color=["#D1E5F0", "#67A9CF", "#2166AC", "#053061"], width=0.6)
for i, k in enumerate(("Q1", "Q2", "Q3", "Q4")): a2.plot([i, i], [Q[k]["p25"], Q[k]["p75"]], color="black", lw=0.9)
assert max(Q[k]["p75"] for k in Q) < 35; a2.set_ylim(0, 35); a2.set_xticks(xq); a2.set_xticklabels(["Lowest", "Second", "Third", "Highest"]); a2.set_xlabel("District quarter of recall")
a2.set_ylabel("Suspicious judgements\nper 1000 recalls")
for a in (a1, a2): a.spines[["top", "right"]].set_visible(False); a.tick_params(labelsize=8)
label(fig, a1, "A", dx=-0.12, dy=0.02); label(fig, a2, "B", dx=-0.12, dy=0.02)
s4 = save(fig, 4)

# Fig 5 포레스트
LAB = N["LAB"]; ORD = N["HYP"]
MOD = [("Principal model", lambda v: N["main"][v][:3], "o", "#000000"),
       ("Province-by-year effect", lambda v: N["s41"].get(("C4_sido_year_iid", v), (None,))[:3], "D", "#B2182B"),
       ("Without 2020", lambda v: N["sens"]["sx20"].get(v, (None,))[:3], "s", "#E08214"),
       ("Crude expected recalls", lambda v: N["sens"]["s8"].get(v, (None,))[:3], "v", "#8073AC"),
       ("Care outside district and beds added", lambda v: N["sens"]["si"].get(v, (None,))[:3], "^", "#2D004B"),
       ("Knorr-Held best interaction", lambda v: N["s43"].get((N["BEST_KH"], v), (None,))[:3], "P", "#2166AC")]
VALS = [t for v in ORD for _, f, _, _ in MOD if (t := f(v)) and t[0] is not None]; lo_all = min(t[1] for t in VALS); hi_all = max(t[2] for t in VALS)
fig, ax = plt.subplots(figsize=(W, 5.6)); fig.subplots_adjust(left=0.36, right=0.98, top=0.97, bottom=0.23)
off = np.linspace(-0.36, 0.36, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, mk, fc), o in zip(MOD, off):
        t = f(v)
        if not t or t[0] is None: continue
        e, lo_, hi_ = t; ax.plot([lo_, hi_], [i + o] * 2, color=fc, lw=0.9); ax.plot(e, i + o, marker=mk, mfc=fc, mec=fc, ms=3.8, ls="none")
ax.axvline(1, color="#808080", lw=0.6); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v].replace("Moderate-to-vigorous physical activity", "Moderate-to-vigorous activity") for v in ORD], fontsize=8); ax.invert_yaxis()
ax.set_xscale("log"); xt = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=fc, marker=m, mfc=fc, mec=fc, lw=0.9, ms=3.8, label=l) for l, _, m, fc in MOD], loc="upper center", bbox_to_anchor=(0.38, -0.11), ncol=3, frameon=False, fontsize=7.5)
s5 = save(fig, 5)
for k, s, dp in zip((1, 2, 3, 4, 5), (s1, s2, s3, s4, s5), (1200, DPI, DPI, DPI, DPI)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/dp*25.4:.0f} x {s[1]/dp*25.4:.0f} mm")
