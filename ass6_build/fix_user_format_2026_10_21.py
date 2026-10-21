from pathlib import Path
from copy import deepcopy
import re, json, hashlib, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from apply_reference_guide_2026_10_21 import R

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Residential_Intelligence_Proposal_FINAL_TIMELINE_2026-10-21 (1) (2).docx'
OUT = ROOT / 'Residential_Intelligence_Proposal_FORMAT_REVIEWED_2026-10-21.docx'
QA = Path.home() / 'SeminarLab/preboard/document_review/format_corrected'
QA.mkdir(parents=True, exist_ok=True)
d = Document(SOURCE)
original = Document(ROOT / 'ASS6_PROPOSAL_FINAL_2026-10-21/Residential_Intelligence_Proposal_CONTENT_PRESERVED_2026-10-21.docx')
before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
audit = {'source_sha256': before, 'changes': [], 'reference_method': 'Local guide section 1.2.1, pages 11-12: cited-order number'}

def norm(t):
    return re.sub(r'\s+', '', t)

def replace_text(p, text):
    # This is used only on ordinary body text, never on drawings or signatures.
    for child in list(p._p):
        if child.tag != qn('w:pPr'): p._p.remove(child)
    p.add_run(text)

# Recover whitespace from the unchanged wording in the prior editable source.
# Join only user-inserted paragraph splits whose concatenated text is identical.
ps = list(d.paragraphs)
prior = {norm(p.text): p.text.strip() for p in original.paragraphs if len(p.text) > 60 and p.style.name == 'Normal'}
skip = set()
for i in range(37, 175):
    if i in skip or ps[i].style.name != 'Normal' or ps[i]._p.xpath('.//w:drawing'): continue
    for count in [3, 2, 1]:
        group = ps[i:i+count]
        if i+count > 175 or any(p.style.name != 'Normal' or p._p.xpath('.//w:drawing') for p in group): continue
        key = norm(''.join(p.text for p in group))
        if key in prior:
            replace_text(ps[i], prior[key])
            for j in range(i+1, i+count):
                ps[j]._p.getparent().remove(ps[j]._p); skip.add(j)
            audit['changes'].append({'paragraph': i, 'whitespace_restored': True, 'joined_paragraphs': count})
            break

# The user's visual line splits inside this paragraph are not separate ideas.
if not any(i in skip for i in [41,42,43]):
    replace_text(ps[41], ' '.join(ps[i].text.strip() for i in [41,42,43]))
    for i in [42,43]:ps[i]._p.getparent().remove(ps[i]._p);skip.add(i)

# Remaining altered spacing: only whitespace and consistent spelling of existing terms.
for i,p in enumerate(ps):
    if i in skip or not (37 <= i < 175) or p.style.name != 'Normal' or p._p.xpath('.//w:drawing'): continue
    t = p.text.strip().replace('eSenses', 'e-Senses').replace('HomeAssistant', 'Home Assistant')
    t = t.replace('LocalLLM', 'Local LLM').replace('exactmatch', 'exact match').replace('endtoend', 'end-to-end').replace('tradeoff', 'trade-off')
    t = re.sub(r'(?<=[\u0e00-\u0e7f])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?=[\u0e00-\u0e7f])', ' ', t)
    t = re.sub(r'(?<=\S)(?=\[\d)', ' ', t)
    t = re.sub(r'(\[\d+(?:[,\s–-]+\d+)*\])(?=[A-Za-z\u0e00-\u0e7f])', r'\1 ', t)
    t = re.sub(r'\[\d+(?:[,\s–-]+\d+)*\]', lambda m:m[0].replace(' ','\u00a0'),t)
    if t != p.text: replace_text(p,t)

# Body paragraph roles. Retain the user's cover, content order, figures and signature.
for i,p in enumerate(ps):
    if i in skip or i >= 175: continue
    pf=p.paragraph_format
    if p.style.name == 'Heading 1':
        replace_text(p,re.sub(r'^(\d+)\.\s*', r'\1.  ',p.text.strip()))
        pf.alignment=WD_ALIGN_PARAGRAPH.LEFT; pf.keep_with_next=True
    elif p.style.name == 'Heading 2':
        replace_text(p,p.text.strip()); pf.left_indent=Inches(.25); pf.first_line_indent=Inches(0)
        pf.alignment=WD_ALIGN_PARAGRAPH.LEFT; pf.keep_with_next=True
    elif 37 <= i < 175 and p.text.strip() and not p._p.xpath('.//w:drawing'):
        if len(p.text)<140 and re.match(r'^(ตารางที่|ภาพที่)\s*\d',p.text.strip()):
            t=p.text.strip(); m=re.match(r'^((?:ตารางที่|ภาพที่)\s*\d+)\s*(.*)',t)
            replace_text(p,''); p.add_run(m[1]).bold=True; p.add_run('  '+m[2]).bold=False
            pf.alignment=WD_ALIGN_PARAGRAPH.LEFT; pf.left_indent=Inches(0); pf.first_line_indent=Inches(0)
            pf.space_before=Pt(14); pf.space_after=Pt(14); pf.keep_with_next=t.startswith('ตาราง')
        elif p.style.name == 'Normal':
            pf.alignment=WD_ALIGN_PARAGRAPH.THAI_JUSTIFY
            pf.first_line_indent=Inches(.25); pf.left_indent=Inches(0)
            pf.space_before=Pt(0); pf.space_after=Pt(5); pf.widow_control=True
            # Manual line breaks cause artificial stretching under justification.
            for br in p._p.xpath('.//w:br'):
                if br.get(qn('w:type')) not in ['page','column']:
                    br.tag=qn('w:t'); br.text=' '

# Rebuild only the 23 reference entries using already verified, unchanged metadata.
current_to_metadata={1:12,2:1,3:2,4:3,5:4,6:23,7:17,8:5,9:14,10:15,11:16,12:6,13:7,14:8,15:9,16:10,17:18,18:19,19:20,20:21,21:22,22:11,23:13}
refs={int(re.match(r'^\s*\[(\d+)\]',p.text)[1]):p for p in d.paragraphs if re.match(r'^\s*\[\d+\]',p.text)}
assert len(refs)==23
for n,p in refs.items():
    lead,title,tail=R[current_to_metadata[n]]
    replace_text(p,'')
    segments=[(f'[{n}] '+lead,False),(title,n not in [1,5,6]),(tail,False)]
    for text,bold in segments:
        # URLs retain literal punctuation. Else follow the local two-space rule.
        pieces=re.split(r'(https?://\S+)',text)
        for k,part in enumerate(pieces):
            if not k%2:
                part=re.sub(r'([.,:;])\s+',r'\1  ',part)
            for frag in re.split(r'([.,:;])',part):
                if not frag: continue
                r=p.add_run(frag); r.bold=bold and frag not in '.,:;'; r.italic=False
    pf=p.paragraph_format
    pf.left_indent=Inches(.3); pf.first_line_indent=Inches(-.3)
    pf.alignment=WD_ALIGN_PARAGRAPH.LEFT; pf.keep_together=True; pf.keep_with_next=False
    pf.space_before=Pt(0); pf.space_after=Pt(6); pf.line_spacing=1
for i in [198,200]:
    p=ps[i]
    if p._p.getparent() is not None:p._p.getparent().remove(p._p)

# Keep each short table as a whole, including its caption. No reduction in font size.
for table in d.tables:
    table.autofit=False
    for row_index,row in enumerate(table.rows):
        trpr=row._tr.get_or_add_trPr()
        if not trpr.find(qn('w:cantSplit')) is not None:trpr.append(OxmlElement('w:cantSplit'))
        for cell in row.cells:
            for p in cell.paragraphs:
                pf=p.paragraph_format; pf.keep_with_next=row_index<len(table.rows)-1; pf.keep_together=True
                pf.space_before=Pt(0); pf.space_after=Pt(2); pf.line_spacing=1
                for r in p.runs:r.font.size=Pt(14)
    following=table._tbl.getnext()
    if following is not None and following.tag==qn('w:p'):
        from docx.text.paragraph import Paragraph
        Paragraph(following,d._body).paragraph_format.space_before=Pt(14)

# Explicit font slots override prior TH SarabunPSK, including Thai complex-script runs.
parts=[d._element]+[part.element for part in d.part.related_parts.values() if hasattr(part,'element') and part.partname.endswith('.xml')]
for root in parts:
    for rf in root.xpath('.//w:rFonts'):
        for attr in list(rf.attrib):del rf.attrib[attr]
        for slot in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+slot),'TH Sarabun New')
for s in d.styles:
    if s.type in [1,2]:
        s.font.name='TH Sarabun New'
        rf=s.element.get_or_add_rPr().get_or_add_rFonts()
        for slot in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+slot),'TH Sarabun New')
d.styles['Normal'].font.size=Pt(14)
for name,size,bold in [('Title',18,True),('Heading 1',16,True),('Heading 2',14,False)]:
    d.styles[name].font.size=Pt(size); d.styles[name].font.bold=bold
for s in d.sections:
    s.top_margin=s.left_margin=Inches(1.5);s.right_margin=s.bottom_margin=Inches(1);s.header_distance=Inches(1)

# Supply invisible Thai word-break opportunities for reliable layout on this PC.
# They do not change visible wording; the original text is retained in the source.
runs=[r for p in d.paragraphs for r in p.runs if re.search(r'[\u0e00-\u0e7f]',r.text) and not r._r.xpath('.//w:drawing')]
node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
seg=subprocess.run([str(node),str(ROOT/'ass6_build/thai_breaks_2026_10_21.cjs')],input=json.dumps([r.text for r in runs],ensure_ascii=False),text=True,encoding='utf-8',capture_output=True,check=True)
for r,t in zip(runs,json.loads(seg.stdout)):
    assert r.text==t.replace('\u200b','')
    r.text=t

# Thai language tagging is required for Word's Thai word-breaking after text cleanup.
for root in parts:
    for r in root.xpath('.//w:r'):
        rp=r.find(qn('w:rPr'))
        if rp is None:rp=OxmlElement('w:rPr');r.insert(0,rp)
        lang=rp.find(qn('w:lang'))
        if lang is None:lang=OxmlElement('w:lang');rp.append(lang)
        lang.set(qn('w:val'),'th-TH');lang.set(qn('w:bidi'),'th-TH')
for p in ps[:22]:p.paragraph_format.line_spacing=1
for i in [13,15]:
    if not ps[i].text and not ps[i]._p.xpath('.//w:drawing'):
        ps[i]._p.getparent().remove(ps[i]._p)
replace_text(ps[175],'11.  เอกสารอ้างอิง')

# Validate citation numbers and retain figures/table data.
refstart=next(i for i,p in enumerate(d.paragraphs) if p.text.startswith('11.'))
assert len(d.tables)==8
source_tables=[[[''.join(re.findall(r'\S+',c.text)) for c in row.cells] for row in t.rows] for t in Document(SOURCE).tables]
target_tables=[[[''.join(re.findall(r'\S+',c.text)) for c in row.cells] for row in t.rows] for t in d.tables]
assert source_tables==target_tables
d.save(OUT)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before
audit['output']=str(OUT);audit['tables_unchanged']=True
(QA/'format_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(OUT))
