#!/bin/bash
# run_all_jms_brrc.sh — BRRC J Med Screening build (gate → numbers → refs → figures → manuscript → supplement → cover → sanitize → checks)
set -e; cd "$(dirname "$0")"
python3 gate_judgement_brrc.py >/dev/null
python3 numbers_brrc.py >/dev/null
python3 build_refs_brrc.py >/dev/null
python3 figs_jms_brrc.py
python3 build_jms_brrc.py
python3 esm_jms_brrc.py
python3 cover_jms_brrc.py "$@"
python3 sanitize_docx.py --no-anon ../out_jms/Manuscript_JMS_BRRC.docx ../out_jms/Supplementary_Material_JMS_BRRC.docx ../out_jms/STROBE_Checklist_JMS_BRRC.docx ../out_jms/Cover_Letter_JMS_BRRC.docx ../out_jms/Title_Page_JMS_BRRC.docx
python3 check_jms_brrc.py
