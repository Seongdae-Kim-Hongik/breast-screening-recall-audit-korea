# check_cbc_brrc.py — BRRC Clinical Breast Cancer 검사기(2026-11-18, check_er_brrc 이식). 규정 한도·문체·금지 문자열·인용 순서·참고문헌·그림 파일·표 3선.
import os, re, subprocess, json, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out_cbc")
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_cbc.txt")).read().split()); R = []
def ok(name, cond, detail=""): R.append((name, bool(cond), detail))
ok("본문 2000–8000", 2000 <= int(W["body_words"]) <= 8000, W["body_words"]); ok("하이라이트 ≤85자", int(W["highlights_max"]) <= 85, W["highlights_max"]); ok("초록 ≤250", int(W["abstract_words"]) <= 250, W["abstract_words"]); ok("키워드 1–7", 1 <= int(W["keywords"]) <= 7, W["keywords"])
ok("제목 ≤20단어", int(W["title_words"]) <= 20, W["title_words"])
M = os.path.join(OUT, "Manuscript_CBC_BRRC.docx"); subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_brrc_chkc", "--convert-to", "pdf", "--outdir", OUT, M], capture_output=True)
T = subprocess.run(["pdftotext", M.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
body = T[:T.find("\nReferences\n")]
ok("1인칭 0", not re.search(r"\b(we|our|us)\b", body, re.I), re.findall(r"\b(?:we|our|us)\b", body, re.I)[:5])
ok("em-dash 0", "—" not in T); ok("[확인]·자리표시 0", not re.search(r"\[확인|\[ZENODO|XXX|TODO", T))
ok("한글 0", not re.search(r"[가-힣]", T))
for h in ("Introduction:", "Patients and Methods:", "Results:", "Conclusion:", "Introduction", "Materials and Methods", "Discussion", "Conclusion", "CRediT authorship contribution statement", "Funding", "Declaration of competing interest", "Ethics approval", "Data availability", "Declaration of generative AI"): ok(f"절 {h}", (h in T))
ok("Zenodo DOI 본문", re.search(r"10\.5281/zenodo\.\d+", T))
ok("BI-RADS 매핑", "categories 0 and 3" in T.replace("\n", " "))
refs = T[T.find("\nReferences\n"):T.find("\nFigure captions\n")]
ok("참고문헌 github·zenodo 0", not re.search(r"(?i)github|zenodo", refs))
ok("제목 쌍점 0", ":" not in T.split("\n")[0])
r = subprocess.run(["python3", os.path.expandvars("$ST_DATA_ROOT") + "/G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py", M], capture_output=True, text=True)
ok("인용 순서 PASS", "FAIL" not in r.stdout and r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])
z = zipfile.ZipFile(M).read("word/document.xml").decode("utf8"); ok("표 세로줄 0(3선)", 'w:left w:val="single"' not in z and 'w:insideV w:val="single"' not in z)
for k in range(1, 6): ok(f"Figure_{k}.tif", os.path.exists(os.path.join(OUT, "Figures", f"Figure_{k}.tif")))
ok("p 값 대문자 P 0", not re.search(r"\bP\s*[<=>]\s*0", body))
for n, c, d in R: print(("✅" if c else "❌"), n, d)
print("PASS" if all(c for _, c, _ in R) else "FAIL", f"{sum(c for _, c, _ in R)}/{len(R)}")
open(os.path.join(OUT, "check_cbc.txt"), "w").write("\n".join(f"{'PASS' if c else 'FAIL'} {n} {d}" for n, c, d in R) + "\n")
