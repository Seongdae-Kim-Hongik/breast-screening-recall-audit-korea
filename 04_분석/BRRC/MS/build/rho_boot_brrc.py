# rho_boot_brrc.py — 14-year district SRRs of recall vs suspicious judgements: Spearman rho with 5000 bootstrap resamples of districts (seed 20261118).
import numbers_brrc as NB, pandas as pd, numpy as np, os, json
from scipy.stats import spearmanr
g = pd.read_csv(os.path.join(NB.RS, "S50D_aux_district.csv"), encoding="utf-8-sig")
r = spearmanr(g.SIR, g.SIR_sp).correlation; rng = np.random.default_rng(20261118); bs = []
for _ in range(5000):
    i = rng.integers(0, len(g), len(g)); bs.append(spearmanr(g.SIR.values[i], g.SIR_sp.values[i]).correlation)
lo, hi = np.percentile(bs, [2.5, 97.5])
json.dump(dict(rho=r, lo=lo, hi=hi, n=len(g), sp_median=float(g.sp.median()), seed=20261118, B=5000), open(os.path.join(NB.RS, "S50R_rho_bootstrap.json"), "w"))
print(round(r, 3), round(lo, 3), round(hi, 3))
