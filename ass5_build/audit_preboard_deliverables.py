"""Read-only consistency checks for the final presentation, script and proposal."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PPTX=ROOT/'ass5_output/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pptx'
SCRIPT=ROOT/'ass5_output/Residential_Intelligence_Presentation_Script_REVIEWED_2026-10-18.md'
DOCX=ROOT/'ass6_output/Residential_Intelligence_Computer_Project_Proposal_REVIEWED_2026-10-18.docx'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    files=[PPTX,PPTX.with_suffix('.pdf'),SCRIPT,DOCX,DOCX.with_suffix('.pdf')]
    assert all(p.exists() for p in files),'Missing final deliverable'
    ocr=read(ROOT/'reports/preboard/single_pass_ocr.json')
    llm=read(ROOT/'reports/preboard/single_pass_llm.json')
    pc=read(ROOT/'reports/preboard/pc_transport_profile.json')
    assert llm['complete'] and llm['attempts']==288
    assert pc['run_id']=='pc-delivery-profile-engineering-v3' and pc['failures']==0 and pc['attempts']==9
    with zipfile.ZipFile(PPTX) as z:
        names=sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda n:int(re.search(r'slide(\d+)',n)[1]))
        slides=[' '.join(ET.fromstring(z.read(n)).itertext()) for n in names]
        notes=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        matrix=ET.fromstring(z.read('ppt/slides/slide17.xml')).find('.//a:tbl',ns)
        matrix_rows=[[''.join(c.itertext()) for c in r.findall('a:tc',ns)] for r in matrix.findall('a:tr',ns)]
    assert len(slides)==len(notes)==21
    script=SCRIPT.read_text(encoding='utf-8')
    assert [int(x) for x in re.findall(r'^(\d+)\. \*\*',script,re.M)]==list(range(1,22))
    doc=Document(DOCX)
    report='\n'.join([p.text for p in doc.paragraphs]+[c.text for t in doc.tables for r in t.rows for c in r.cells])
    text='\n'.join(slides)
    for identifier in ['SCS3-4','SCS3','673380267-4','673380270-5']:
        assert identifier in text and identifier in report,identifier
    for key in ['easyocr','tesseract']:
        value=f"{100*ocr['summaries']['all_eligible'][key]['micro_cer']:.2f}%"
        assert value in text and value in report and value in script,value
    assert str(ocr['saved_photos']) in slides[12] and str(ocr['scorable_photos']) in slides[12]
    assert str(ocr['excluded_photos']) in slides[12]
    assert '288/288' in slides[16] and '288' in report
    for phrase in ['ยังไม่ได้ทดลอง','Home Assistant','Q4_K_M']:
        assert phrase in text and phrase in report,phrase
    assert not any('ยังไม่รัน' in s for s in slides)
    assert len(doc.tables)==8
    models=['qwen3-0.6B-Q8_0','qwen3-0.6B-Q4_K_M','qwen3-1.7B-Q8_0','qwen3-1.7B-Q4_K_M']
    for mi,model in enumerate(models):
        for si,source in enumerate(['owner_text','tesseract']):
            for gi,grammar in enumerate([False,True]):
                g=next(g for g in llm['groups'] if (g['model'],g['source'],g['grammar'])==(model,source,grammar))
                assert g['attempts']==18 and g['photos']==6
                assert matrix_rows[mi+1][si*2+gi+1]==f"{g['schema_valid']}/18"
                cells=doc.tables[4+si].rows[1+mi*2+gi].cells
                assert [c.text for c in cells[2:]]==[f"{g['parse_valid']}/18",f"{g['schema_valid']}/18",f"{g['median_seconds']:.2f}",f"{g['max_model_process_tree_rss_bytes']/2**30:.2f}"]
    seconds=f"{pc['summaries']['automated_window_to_ha_observed_seconds']['median']:.3f}"
    rss=f"{pc['summaries']['windows_full_host_rss_bytes']['median']/2**30:.3f}"
    assert all(value in body for value in [seconds,rss] for body in [text,report,script])
    available=doc.sections[0].page_width-doc.sections[0].left_margin-doc.sections[0].right_margin
    assert all(sum(c.width for c in t.columns)<=available+635 for t in doc.tables)
    headings=[p.text for p in doc.paragraphs if p.style.name=='Heading 1']
    assert len(headings)==11,headings
    literature=['Cai','Husom','Moon','Yin','Oloko-Oba','Zheng','Giedra','Hu','Rivkin','Sawalha','Serepas']
    assert all(name in report for name in literature)
    for s in doc.sections:
        assert abs(s.top_margin.inches-1.5)<.02 and abs(s.left_margin.inches-1.5)<.02
        assert abs(s.right_margin.inches-1)<.02 and abs(s.bottom_margin.inches-1)<.02
    finalizer=read(ROOT/'.codex-finalizer'/f'{PPTX.name}.validation.json')
    assert finalizer['finalSha256']==sha(PPTX)
    pdf_pages={p.name:len(PdfReader(p).pages) for p in [PPTX.with_suffix('.pdf'),DOCX.with_suffix('.pdf')]}
    assert pdf_pages[PPTX.with_suffix('.pdf').name]==21
    review=read(Path.home()/'SeminarLab/preboard/document_review/revision/visual_signoff.json')
    for p in [PPTX.with_suffix('.pdf'),DOCX.with_suffix('.pdf')]:
        item=review[p.name]
        assert item['sha256']==sha(p) and item['pages_reviewed']==list(range(1,pdf_pages[p.name]+1))
        assert item['unresolved_findings']==[]
    result={'status':'pass','scope':'Available PC evidence and Ass5/Ass6 delivery; deferred experiments are not marked complete',
            'artifacts':{p.relative_to(ROOT).as_posix():sha(p) for p in files},'pdf_pages':pdf_pages,
            'slides':21,'script_sections':21,'proposal_main_sections':len(headings),'proposal_tables':len(doc.tables),
            'references':len([p for p in doc.paragraphs if re.match(r'^\[\d+\]',p.text)]),
            'visual_review':review,'deferred':['JSON semantic accuracy','fresh scene challenge','board NPU and energy'],
            'evidence_sha256':{name:sha(ROOT/'reports/preboard'/name) for name in ['single_pass_ocr.json','single_pass_llm.json','pc_transport_profile.json']}}
    (ROOT/'reports/preboard/deliverable_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Final cross-file audit passed',pdf_pages)


if __name__=='__main__':main()
