# cover_cbc_brrc.py — BRRC Clinical Breast Cancer 커버레터(1쪽, 단독 저자 비인칭, 김성대 명의)(2026-11-18).
#  커버레터: 저널 적합성, 단독 저자 승인 진술. 자료 중복·이전 투고 고지 금지(저자 결정). 제외 심사자는 포털 칸에만. Zenodo 공개 DOI만. --draft면 DOI 자리표시자 허용.
import os, re, sys, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
from build_cbc_brrc import N, TITLE, ZENODO, ADDRESS, IRB, IRB2, RB
from british import brit
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out_cbc"); DRAFT = "--draft" in sys.argv
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_cbc.txt")).read().split())
if not DRAFT: assert ZENODO.startswith("10.5281/zenodo."), "공개 DOI 없음(투고 전 게이트)"
def mk(lines, fp, title):
    d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
    for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
    gap = False
    for t in lines:
        if t == "": gap = True; continue
        b = t.startswith("**"); t = t.strip("*")
        p = d.add_paragraph(); r = p.add_run(brit(t)); r.bold = b
        if gap: p.paragraph_format.space_before = Pt(10); gap = False
    d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = title; d.core_properties.comments = ""
    d.save(fp); subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_brrc_clc", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
    return subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
q = N["ppv_q"]; AX = N["aux"]
_d = datetime.date.today(); cl = [f"{_d.day} {_d:%B} {_d.year}", "The Editor-in-Chief", "Clinical Breast Cancer", "",
      "Dear Editor,",
      f"Please find enclosed the manuscript entitled \"{TITLE}\" by Seongdae Kim, for consideration as an Original Study in Clinical Breast Cancer.",
      f"Recall is a core audit measure of a breast screening programme, and its variation is usually attributed either to breast density in the women screened or to differences in reading. This study examines recall in the national programme of the Republic of Korea across all {N['n_districts']} districts over 2011–2024, using published data on {N['exam_total']:,} screening mammograms. "
      f"Recall formed a stable, spatially structured district pattern that age-standardisation barely changed and that persisted after adjustment for ten measured district characteristics, and districts with more recalls did not record more examinations judged suspicious for cancer at screening (Spearman ρ {RB['rho']:.2f}, 95% bootstrap interval {RB['lo']:.2f} to {RB['hi']:.2f}). Suspicious judgements are screening classifications, not confirmed cancers.",
      "The findings bear directly on clinical practice in breast cancer detection. Recall decides which women undergo diagnostic work-up, and the study shows that its regional variation is not explained by district proxies for the composition of screened women and is not matched by more suspicious judgements. It documents how the programme's judgement categories map to BI-RADS and how their national composition changed over 14 years, and identifies geographic variation in recall that warrants audit linking recall to reading facilities and confirmed cancers. "
      f"The study used only published aggregate statistics; the Institutional Review Board of Hongik University approved it ({IRB}) and its continuing review ({IRB2}). The manuscript is original, has not been published and is not under consideration elsewhere, and the sole author has seen and approved the submitted version.",
      f"The main text contains {int(W['body_words'])} words, with a structured abstract of {int(W['abstract_words'])} words, two tables, five figures and {W['refs']} references. Highlights, a supplementary file and the STROBE checklist are provided. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript, reviewed and edited all output, and takes full responsibility for the content. No other writing or editing assistance was received.",
      "Thank you for considering this manuscript.", "", "Yours sincerely,", "",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "Email: kimsd@hongik.ac.kr"]
cl = [re.sub(r"(?<![\w.])-(?=\d)", "\u2212", x) for x in cl]
fp = os.path.join(OUT, "Cover_Letter_CBC_BRRC.docx"); txt = mk(cl, fp, "Cover Letter")
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-?\s*202611-?\s*HR-040", txt) and not re.search(r"(?i)competing|overlap|previously submitted|reject|token|private link", txt), "문체·IRB·금지 항목"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages, "draft" if DRAFT else "")
