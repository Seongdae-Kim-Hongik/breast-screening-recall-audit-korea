#!/bin/bash
# run_all_cbc_brrc.sh — BRRC Clinical Breast Cancer build (gate → numbers → refs → figures → manuscript → supplement → cover → sanitize → checks)
set -e; cd "$(dirname "$0")"
python3 gate_judgement_brrc.py >/dev/null
python3 numbers_brrc.py >/dev/null
python3 rho_boot_brrc.py >/dev/null
python3 build_refs_brrc.py >/dev/null
python3 figs_cbc_brrc.py
python3 build_cbc_brrc.py
python3 esm_cbc_brrc.py
python3 cover_cbc_brrc.py "$@"
python3 sanitize_docx.py --no-anon ../out_cbc/Manuscript_CBC_BRRC.docx ../out_cbc/Supplementary_Material_BRRC.docx ../out_cbc/STROBE_Checklist_BRRC.docx ../out_cbc/Cover_Letter_CBC_BRRC.docx ../out_cbc/Title_Page_CBC_BRRC.docx ../out_cbc/Highlights_CBC_BRRC.docx
python3 check_cbc_brrc.py
