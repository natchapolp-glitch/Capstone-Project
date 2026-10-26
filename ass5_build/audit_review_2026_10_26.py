"""Read-only review of slide text, note sources, and presentation evidence."""
import json
import re
import statistics
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.codex-finalizer/review-complete-2026-10-26'
OUT.mkdir(parents=True, exist_ok=True)
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
source = ROOT / 'PRESENTATION_READY_2026-10-26/Ass5_REVIEWED_2026-10-26.pptx'
with zipfile.ZipFile(source) as z:
    slides = []
    for i in range(1, 22):
        text = '\n'.join(ET.fromstring(z.read(f'ppt/slides/slide{i}.xml')).itertext())
        # Only a:t contains visible copy, excluding geometry data.
        text = '\n'.join(t.text or '' for t in ET.fromstring(z.read(f'ppt/slides/slide{i}.xml')).findall('.//a:t', NS))
        note = '\n'.join(t.text or '' for t in ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')).findall('.//a:t', NS))
        slides.append({'slide': i, 'text': text, 'original_notes': note})
(OUT / 'source_content.json').write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding='utf-8')
ocr = json.loads((ROOT/'reports/preboard/single_pass_ocr.json').read_text(encoding='utf-8'))
timing = json.loads((ROOT/'reports/preboard/pc_transport_profile.json').read_text(encoding='utf-8'))
llm = json.loads((ROOT/'reports/preboard/single_pass_llm.json').read_text(encoding='utf-8'))
assert ocr['candidate_photos'] == ocr['saved_photos'] == 59
assert ocr['scorable_photos'] == 24 and ocr['excluded_photos'] == 35
assert round(ocr['summaries']['all_eligible']['easyocr']['micro_cer']*100,2)==82.36
assert round(ocr['summaries']['all_eligible']['tesseract']['micro_cer']*100,2)==94.57
assert round(timing['summaries']['automated_window_to_ha_observed_seconds']['median'],3)==10.758
assert timing['attempts']==9 and timing['source_photos']==3
print(json.dumps({'slides':len(slides),'ocr_and_timing_checks':'passed','llm_top_level_keys':list(llm),'slide17':slides[16]['text'],'note_example':slides[16]['original_notes']},ensure_ascii=True,indent=2))
