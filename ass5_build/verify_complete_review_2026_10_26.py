import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.codex-finalizer/review-complete-2026-10-26'
FINAL=ROOT/'PRESENTATION_READY_2026-10-26/Ass5_10MIN_REVIEWED_v2_2026-10-26.pptx'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
llm=json.loads((ROOT/'reports/preboard/single_pass_llm.json').read_text(encoding='utf-8'))
sections=json.loads((OUT/'speaking_sections.json').read_text(encoding='utf-8'))
checks={}
with zipfile.ZipFile(FINAL) as z:
    for section in sections:
        n=section['slide']
        note='\n'.join(t.text or '' for t in ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{n}.xml')).findall('.//a:t',NS))
        assert section['text'] in note, f'Notes mismatch on slide {n}'
    table=ET.fromstring(z.read('ppt/slides/slide17.xml')).find('.//a:tbl',NS)
    matrix=[[''.join(t.text or '' for t in cell.findall('.//a:t',NS)) for cell in row.findall('a:tc',NS)] for row in table.findall('a:tr',NS)]
    for row in matrix[1:]:
        model='qwen3-'+row[0]
        for col,(source,grammar) in enumerate([('owner_text',False),('owner_text',True),('ocr_text',False),('ocr_text',True)],1):
            matches=[g for g in llm['groups'] if g['model']==model and g['source']==source and g['grammar']==grammar]
            if not matches and source=='ocr_text':
                matches=[g for g in llm['groups'] if g['model']==model and g['source']!='owner_text' and g['grammar']==grammar]
            assert len(matches)==1,(model,source,grammar)
            g=matches[0]
            assert row[col]==f"{g['schema_valid']}/{g['attempts']}",(model,row[col],g)
checks['speaker_notes_match_all_21_sections']=True
checks['llm_table_all_16_cells_match_saved_evidence']=True
checks['llm_attempts']=llm['attempts']
checks['same_pixels_as_previous_native_pdf']=[]
checks['changed_pixels']=[]
for n in range(1,22):
    old=Image.open(ROOT/f'.codex-finalizer/review-2026-10-26/native-{n:02}.png').convert('RGB')
    new=Image.open(OUT/f'native-{n:02}.png').convert('RGB')
    key='same_pixels_as_previous_native_pdf' if old.size==new.size and ImageChops.difference(old,new).getbbox() is None else 'changed_pixels'
    checks[key].append(n)
checks['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [FINAL,FINAL.with_suffix('.pdf')]}
checks['human_rehearsal_timing']='not measured; 540-second plan includes 120-second demo'
(OUT/'content_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=True,indent=2))
