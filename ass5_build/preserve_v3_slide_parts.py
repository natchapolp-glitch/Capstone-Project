"""Preserve the original deck package except for the Artifact Tool-authored note body."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import json

root=Path(__file__).resolve().parents[1]
build=root/'.codex-finalizer/recorded-demo-v3'
source=root/'PRESENTATION_READY_2026-10-26/Ass5_10MIN_REVIEWED_v2_2026-10-26.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
part='ppt/notesSlides/notesSlide18.xml'
with ZipFile(source) as original, ZipFile(build/'artifact-notes.pptx') as authored:
    before=ET.fromstring(original.read(part)); after=ET.fromstring(authored.read(part))
    def body(tree):
        return tree.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=ns)[0]
    replacement=body(after)
    actual='\n'.join(''.join(p.itertext()) for p in replacement.findall('a:p',ns))
    assert 'RECORD_DEMO_SCRIPT.md' in actual and 'อ่านภาพจริง' in actual
    oldbody=body(before); oldbody.getparent().replace(oldbody,replacement)
    with ZipFile(build/'candidate.pptx','w',ZIP_DEFLATED) as dest:
        for item in original.infolist():
            dest.writestr(item,ET.tostring(before,xml_declaration=True,encoding='UTF-8',standalone=True) if item.filename==part else original.read(item.filename))
with ZipFile(source) as a, ZipFile(build/'candidate.pptx') as b:
    changes=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    assert changes==[part],changes
(build/'package-preservation.json').write_text(json.dumps({'changed_parts':changes,'all_visible_slide_parts_unchanged':True},indent=2),encoding='utf-8')
print('Only note 18 changed; all visible slides, media, tables, masters and other notes preserved byte-for-byte.')
