# build_refs_brrc.py — BRRC 참고문헌 메타데이터 캐시(refs_brrc.json). 키 = draft md + build_cbc_brrc.py METHODS의 [@key] (11/18 재투고판).
#  주제 문헌 = refs/brrc_refs_verified.csv(PubMed efetch 11/13, 초록 포함), 방법 문헌 = SKND 검증 캐시에서 복사.
import os, re, json, csv
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); AN = os.path.dirname(os.path.dirname(MS))
src = open(os.path.join(HERE, "build_cbc_brrc.py"), encoding="utf-8").read() + open(os.path.join(MS, "draft", "03_manuscript.md"), encoding="utf-8").read()
src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
keys = sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")}); keys = [k for k in keys if re.fullmatch(r"[a-z][a-z0-9]*", k)]
OLD = json.load(open(os.path.join(AN, "SKND/MS/build/refs_sknd.json"), encoding="utf-8"))
V = {r["key"]: r for r in csv.DictReader(open(os.path.join(MS, "refs", "brrc_refs_verified.csv"), encoding="utf-8"))}
def fullp(p):
    m = re.match(r"^(\d+)-(\d+)$", str(p))
    if not m: return p
    a, b = m.groups(); return p if len(b) >= len(a) else f"{a}-{a[:len(a)-len(b)]+b}"
out = {}
import urllib.request, time
ids = ",".join(V[k]["pmid"] for k in keys if k in V)
d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ids, timeout=60))["result"]
for k in keys:
    if k in V:
        r = d[V[k]["pmid"]]; au = [a["name"] for a in r["authors"] if a.get("authtype", "Author") == "Author"] or [a["name"] for a in r["authors"]]
        out[k] = dict(type="journal", authors=[a.title() if a.isupper() else a for a in au], title=r["title"].rstrip("."), journal=r["source"].replace(".", ""), year=int(r["pubdate"][:4]), vol=r.get("volume", ""), issue=r.get("issue", ""),
                      pages=fullp(r.get("pages", "")), doi=V[k]["doi"], pmid=V[k]["pmid"], verified="PubMed esummary " + time.strftime("%Y-%m-%d"))
    elif k in OLD: out[k] = OLD[k]
miss = [k for k in keys if k not in out]; assert not miss, miss
json.dump(out, open(os.path.join(HERE, "refs_brrc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(keys), "keys")
for k in keys: v = out[k]; print(k, "|", v.get("journal"), v.get("year"), v.get("vol"), v.get("pages"), v.get("doi"), "|", str(v.get("title"))[:60])
