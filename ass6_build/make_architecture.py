from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'ass6_assets' / 'system_architecture.png'
OUT.parent.mkdir(exist_ok=True)
im = Image.new('RGB', (1700, 630), '#ffffff')
d = ImageDraw.Draw(im)
font_dir = Path('C:/Windows/Fonts')
font_file = font_dir / 'arial.ttf'
bold_file = font_dir / 'arialbd.ttf'
f32 = ImageFont.truetype(str(bold_file), 32)
f29 = ImageFont.truetype(str(font_file), 29)
f24 = ImageFont.truetype(str(font_file), 24)

def panel(xy, fill, title, detail='', tc='#ffffff'):
    d.rounded_rectangle(xy, radius=22, fill=fill)
    x0,y0,x1,y1=xy
    d.text((x0+26,y0+24), title, font=f32, fill=tc)
    if detail: d.text((x0+26,y0+80), detail, font=f24, fill=tc)

def arrow(x1,y1,x2,y2):
    d.line((x1,y1,x2,y2),fill='#227b99',width=6)
    if x2>x1:
        d.polygon([(x2,y2),(x2-16,y2-10),(x2-16,y2+10)],fill='#227b99')
    elif y2>y1:
        d.polygon([(x2,y2),(x2-10,y2-16),(x2+10,y2-16)],fill='#227b99')

d.rounded_rectangle((490,20,1210,110),radius=22,fill='#1d2a5d')
d.text((552,45),'Home Digital Nervous System',font=f32,fill='#ffffff')
d.line((850,110,850,150),fill='#227b99',width=6)
d.line((275,150,1425,150),fill='#227b99',width=6)
for x in (275,850,1425): d.line((x,150,x,183),fill='#227b99',width=6)
panel((35,183,515,310),'#006289','e-Eye','Visual sensing | PC pilot')
panel((610,183,1090,310),'#7794a4','e-Nose','Gas / VOC | future')
panel((1185,183,1665,310),'#7794a4','e-Skin','Weight / touch | future')
arrow(275,310,275,383)
d.text((45,340),'Initial study path',font=f29,fill='#1d2a5d')
panel((35,383,395,535),'#e6f1f4','Image / YOLO / OCR','PC pilot',tc='#1d2a5d')
arrow(403,459,464,459)
panel((470,383,850,535),'#e6f1f4','Local LLM / JSON','planned',tc='#1d2a5d')
arrow(858,459,919,459)
panel((925,383,1380,535),'#e6f1f4','MQTT / Home Assistant','future integration',tc='#1d2a5d')
d.text((42,574),'Conceptual architecture; NPU deployment is not yet measured.',font=f24,fill='#596a75')
im.save(OUT)
print(OUT.name)
