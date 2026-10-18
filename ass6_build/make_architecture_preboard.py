"""Render the source architecture with readable labels at A4 report width."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ass6_assets/system_architecture_preboard.png'
S=2
im=Image.new('RGB',(1200*S,820*S),'white'); d=ImageDraw.Draw(im)
fontdir=Path('C:/Windows/Fonts')
def font(size,bold=False):
    return ImageFont.truetype(str(fontdir/('arialbd.ttf' if bold else 'arial.ttf')),size*S)
def box(xy,fill): d.rounded_rectangle(tuple(int(v*S) for v in xy),radius=15*S,fill=fill)
def text(xy,value,size=30,bold=False,fill='#1d2a5d'):
    d.multiline_text(tuple(int(v*S) for v in xy),value,font=font(size,bold),fill=fill,spacing=8*S)
def line(points,width=4): d.line([(x*S,y*S) for x,y in points],fill='#227b99',width=width*S)
def arrow(x1,y1,x2,y2):
    line([(x1,y1),(x2,y2)])
    tip=[(x2,y2),(x2-12,y2-8),(x2-12,y2+8)] if x2>x1 else [(x2,y2),(x2-8,y2-12),(x2+8,y2-12)]
    d.polygon([(x*S,y*S) for x,y in tip],fill='#227b99')
box((250,20,950,105),'#1d2a5d')
text((300,43),'Home Digital Nervous System',33,True,'white')
line([(600,105),(600,145),(200,145),(200,185)])
line([(600,145),(1000,145),(1000,185)])
line([(600,145),(600,185)])
for x,title,detail,fill in [(25,'e-Eye','Visual sensing\nPC pilot','#006289'),(425,'e-Nose','Gas / VOC\nFuture extension','#7794a4'),(825,'e-Skin','Weight / touch\nFuture extension','#7794a4')]:
    box((x,185,x+350,365),fill);text((x+22,205),title,36,True,'white');text((x+22,265),detail,30,False,'white')
arrow(200,365,200,450)
text((230,390),'e-Eye study path',28)
for x,title,detail in [(25,'Image\nYOLO / OCR','PC pilot'),(425,'Local LLM\nJSON','PC format / timing'),(825,'MQTT\nHome Assistant','PC integration')]:
    box((x,450,x+350,665),'#e6f1f4');text((x+22,475),title,34,True);text((x+22,595),detail,29)
arrow(378,550,420,550);arrow(778,550,820,550)
text((25,705),'JSON content accuracy: pending\nNPU and energy measurements: pending',30,False,'#596a75')
im.save(OUT);print(OUT)
