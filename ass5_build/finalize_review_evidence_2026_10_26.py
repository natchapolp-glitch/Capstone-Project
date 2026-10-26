"""Summarize the final unmerged run and verify local review links."""
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
run='run-20261026-185448'
result=ROOT/'DEMO_PRESENTATION_2026-10-21/robot_results'/run
tree=ET.parse(result/'output.xml')
tests=[{'name':t.attrib['name'],'status':t.find('status').attrib['status']} for t in tree.findall('.//suite/test')]
assert len(tests)==7 and all(t['status']=='PASS' for t in tests)
transport=json.loads((result/'transport_evidence.json').read_text(encoding='utf-8'))
files=[ROOT/'README.md',ROOT/'DEMO_PRESENTATION_2026-10-21/ROBOT_TEST_README.md',
       ROOT/'PRESENTATION_READY_2026-10-26/START_HERE.md',
       ROOT/'PRESENTATION_READY_2026-10-26/REVIEW_RESULTS_2026-10-26.md',
       ROOT/'HANDOFF_PRESENTATION_REVIEW_2026-10-26.md']
missing=[]
for path in files:
    for url in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' not in url and not url.startswith('#') and not (path.parent/url.split('#')[0]).exists():
            missing.append({'file':path.name,'link':url})
assert not missing,missing
checks=json.loads((ROOT/'.codex-finalizer/review-complete-2026-10-26/content_verification.json').read_text(encoding='utf-8'))
report={'date':'2026-10-26','robot_run':run,'tests':tests,'unmerged_single_run':True,
        'content_verification':checks,'transport':transport,
        'antivirus_condition':'owner reported disabling antivirus before runtime restoration; protection-enabled operation not tested',
        'quarantine_evidence':{'source':'AVG chest/index.xml','filename':'llama-server.exe','detection':'IDP.Generic'},
        'runtime_archive_sha256':'f78eded047061a3f86372db426797400a2f1bb0ec37868d5927dd820eb3386c0',
        'runtime_executable_sha256':'12c015512d280661fc53ed59f2d8f5cdba3ca9b6948a891eab3087cd93b1154d',
        'unfinished':['human timed rehearsal','recorded and checked demo clip if chosen','native slideshow/video playback','protection-enabled runtime check']}
(ROOT/'reports/preboard/presentation_review_2026-10-26.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'robot_passed':len(tests),'local_links_missing':missing,'receipt_id':transport['receipt_id']},indent=2))
