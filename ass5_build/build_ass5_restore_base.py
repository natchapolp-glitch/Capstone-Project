from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'ass5_output' / 'Residential_Intelligence_Project_Progress_READY_2026-10-18.pptx'
EDA = ROOT / 'ass5_assets' / 'eda_itemized_59.png'
DEMO_SOURCE = Path.home() / 'SeminarLab' / 'yolo_expanded' / 'val' / 'images' / 'R4F4EA934251E.jpg'
DEMO_RESULT = ROOT / 'ass5_assets' / 'demo_receipt_detection.jpg'
OUT.parent.mkdir(exist_ok=True)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
NAVY = RGBColor(29, 42, 93)
BLUE = RGBColor(0, 98, 137)
TEAL = RGBColor(19, 126, 154)
MINT = RGBColor(225, 241, 238)
PALE = RGBColor(242, 246, 248)
INK = RGBColor(29, 47, 62)
MUTED = RGBColor(87, 105, 117)
ORANGE = RGBColor(192, 92, 43)
WHITE = RGBColor(255, 255, 255)
FONT = 'Tahoma'

def box(slide, x, y, w, h, color, radius=False, border=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    if border:
        sh.line.color.rgb = border
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    return sh

def line(slide, x1, y1, x2, y2, color=TEAL, width=1.4):
    sh = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb = color; sh.line.width = Pt(width)
    return sh

def txt(slide, value, x, y, w, h, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = sh.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.02)
    tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(value.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item; p.alignment = align
        p.font.name = FONT; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
        p.space_after = Pt(4)
    return sh

def base(title, subtitle='', dark=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY if dark else WHITE
    fg = WHITE if dark else NAVY
    txt(s,title,.68,.42,12,.62,28,fg,True)
    if subtitle: txt(s,subtitle,.7,1.12,11.9,.5,15,WHITE if dark else MUTED)
    line(s,.7,7.04,12.65,7.04,TEAL if dark else RGBColor(211,223,231),1)
    txt(s,'โครงงานคอมพิวเตอร์ | รายงานความก้าวหน้า | 18 ต.ค. 2569',.72,7.10,10,.22,9,WHITE if dark else MUTED)
    txt(s,str(len(prs.slides)),12.25,7.10,.35,.22,9,WHITE if dark else MUTED,align=PP_ALIGN.RIGHT)
    return s

def tag(slide, value, x, y, w, color=TEAL):
    box(slide,x,y,w,.38,color,radius=True)
    txt(slide,value,x+.1,y+.055,w-.2,.27,13,WHITE,True,PP_ALIGN.CENTER)

# 1. Cover, in the visual language of the original nine-slide deck.
s=prs.slides.add_slide(BLANK); s.background.fill.solid(); s.background.fill.fore_color.rgb=NAVY
box(s,10.6,0,2.73,3.1,BLUE)
box(s,0,6.25,2.2,1.25,TEAL)
txt(s,'การนำเสนอความก้าวหน้าโครงงานคอมพิวเตอร์',.73,.58,11.7,.55,21,WHITE,True)
txt(s,'การพัฒนาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัย\nเพื่อสกัดและวิเคราะห์ข้อมูลห่วงโซ่อุปทานในครัวเรือน\nด้วยปัญญาประดิษฐ์ประมวลผลเฉพาะถิ่น',.73,1.45,11.8,2.25,28,WHITE,True)
line(s,.75,4.15,5.9,4.15,TEAL,2)
txt(s,'673380267-4 นายณัชพล เพ็งพล\n673380270-5 นายธนบดี เริ่มรักสกุล',.78,4.47,7.1,.95,18,WHITE)
txt(s,'อาจารย์ที่ปรึกษา ผศ.บุญทรัพย์ ไวคำ',.78,5.62,8.2,.44,17,WHITE)
txt(s,'หมายเลขโครงงาน SCS3-4  |  กลุ่มสอบ SCS3',.78,6.12,8.3,.38,15,WHITE,True)
txt(s,'สาขาวิชาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยขอนแก่น',.78,6.76,10,.28,11,WHITE)
txt(s,'1',12.25,7.10,.35,.22,9,WHITE,align=PP_ALIGN.RIGHT)

# 2. Context. Benefits are goals, not measured comparisons.
s=base('ที่มา: ทำไมจึงออกแบบให้ประมวลผลในบ้าน','ความเป็นส่วนตัว เวลา และต้นทุน เป็นเป้าหมายการออกแบบที่ยังต้องวัดกับระบบจริง')
for x,n,h,b in [(.75,'1','ความเป็นส่วนตัว','ใบซื้อสินค้ามีข้อมูลส่วนบุคคล จึงต้องกำกับการเก็บและส่งต่อ'),(4.9,'2','เวลาและต้นทุน','ตั้งเป้าลดการพึ่งพา Cloud API แต่ยังไม่ได้เปรียบเทียบจริง'),(9.05,'3','ข้อมูลและทรัพยากร','ภาพต่างร้าน ภาษา และแสง ต้องประมวลผลบนเครื่องจำกัด')]:
    box(s,x,2.04,3.55,2.76,PALE,radius=True)
    tag(s,n,x+.2,2.25,.51,BLUE)
    txt(s,h,x+.22,2.92,3.08,.42,20,NAVY,True)
    txt(s,b,x+.22,3.55,3.08,1.02,16,INK)
txt(s,'แนวทางเดิมยังอยู่: รับภาพ → YOLO/OCR → Local LLM/JSON → MQTT/Home Assistant',.79,5.55,11.8,.76,21,NAVY,True)

# 3. Top-level architecture requested in feedback.
s=base('ภาพรวมระบบประสาทสัมผัสดิจิทัลในบ้าน','e-Senses เป็นกรอบระบบ ส่วนผลทดลองปัจจุบันเจาะลึกที่ e-Eye')
box(s,4.14,1.7,5.05,.73,NAVY,radius=True);txt(s,'Home Digital Nervous System',4.27,1.88,4.8,.3,18,WHITE,True,PP_ALIGN.CENTER)
line(s,6.66,2.43,6.66,2.78,TEAL,2);line(s,2.67,2.78,10.66,2.78,TEAL,2)
for x in (2.67,6.66,10.66): line(s,x,2.78,x,3.05,TEAL,2)
for x,w,title,detail,status,color in [(.72,3.9,'e-Eye','ภาพใบซื้อสินค้า / เอกสาร','ทดลองนำร่อง',BLUE),(4.72,3.9,'e-Nose','ก๊าซ / VOC / กลิ่น','แนวคิดต่อยอด',RGBColor(108,142,161)),(8.72,3.9,'e-Skin','น้ำหนัก / แรงสัมผัส','แนวคิดต่อยอด',RGBColor(108,142,161))]:
    box(s,x,3.05,w,1.76,color,radius=True);txt(s,title,x+.21,3.31,w-.42,.43,24,WHITE,True)
    txt(s,detail,x+.21,3.89,w-.42,.44,16,WHITE)
    txt(s,status,x+.21,4.48,w-.42,.24,12,WHITE)
txt(s,'การศึกษาระยะนี้ใช้ e-Eye เป็นจุดเริ่มต้นของระบบรวม ไม่ได้เปลี่ยนชื่อหรือขอบเขตแนวคิดของทั้งโครงงาน',.75,5.45,11.9,.86,20,NAVY,True)

# 4. Objectives and scope.
s=base('วัตถุประสงค์และขอบเขต','แยกเป้าหมายของโครงงานออกจากสิ่งที่ทดลองแล้ว')
box(s,.74,1.74,5.95,4.5,PALE,radius=True);box(s,6.84,1.74,5.75,4.5,RGBColor(232,243,246),radius=True)
txt(s,'เป้าหมายของโครงงาน',1.02,2.01,5.37,.46,22,NAVY,True)
txt(s,'1  ออกแบบสถาปัตยกรรม e-Senses และ pipeline ในบ้าน\n2  สกัดข้อมูลใบซื้อสินค้าเป็น JSON ที่ตรวจสอบได้\n3  ประเมินความแม่นยำ เวลา และทรัพยากรบน PC ก่อนย้ายสู่อุปกรณ์\n4  ส่งต่อข้อมูลสู่ระบบบ้านอัจฉริยะและวิเคราะห์การใช้เมื่อมีข้อมูลเพียงพอ',1.02,2.62,5.28,3.25,17,INK)
txt(s,'ขอบเขตผลที่มีแล้ว',7.12,2.01,5.15,.46,22,BLUE,True)
txt(s,'ภาพจริงและ EDA\nYOLOv8n ตรวจกรอบเอกสารบน PC CPU\nOCR spot-check 3 ภาพ\nแปลง ONNX เป็น RKNN และรันผ่าน SDK บน PC',7.12,2.65,5.05,2.45,18,INK)
tag(s,'ยังไม่มีผล NPU จริงหรือ JSON/LLM',7.11,5.34,4.88,ORANGE)

# 5. Literature funnel.
s=base('ฐานวิชาการ: คัดกรองวรรณกรรมก่อนออกแบบ','รายงานทบทวนวรรณกรรม 32 หน้าเป็นฐานของสถาปัตยกรรมและคำถามวิจัย')
for i,(n,label,w,color) in enumerate([('57','ค้นพบและติดแท็ก',10.9,BLUE),('37','สถานะ Scopus เบื้องต้น',9.1,TEAL),('35','คงไว้หลังตรวจซ้ำ (มีข้อสงวน 1)',7.4,RGBColor(38,136,160)),('12','ใช้สังเคราะห์ในรายงาน',5.6,NAVY)]):
    x=(13.33-w)/2;y=1.85+i*.93;box(s,x,y,w,.68,color,radius=True)
    txt(s,n,x+.2,y+.11,.65,.39,23,WHITE,True)
    txt(s,label,x+1.03,y+.17,w-1.24,.36,17,WHITE,True)
txt(s,'บทความ 12 ฉบับรวม P5 ที่ใช้สนับสนุนข้ามศาสตร์; อีก 11 ฉบับอยู่ในกรอบสามมิติ',.88,5.88,11.6,.58,16,MUTED)

# 6. Literature synthesis.
s=base('3 มิติของกรอบ Performance Trade-off','ข้อสรุปจากงานทบทวน ใช้กำหนดตัวแปรและตัววัดของการทดลอง')
for x,title,body,ref in [(.76,'Quantization / Hardware','Husom และ Giedra ชี้ให้วัดความถูกต้องคู่กับเวลา RAM และพลังงาน','P1–P4, P6, P10'),(4.94,'Structured Output','SGLang เป็นฐานคิดเรื่อง grammar; ต้องตรวจทั้ง schema และค่าจากใบเสร็จ','P8–P9'),(9.12,'Smart Home / IoT','ESP32/MQTT และอนุกรมเวลาเป็นฐานชั้นปลายน้ำเมื่อมีข้อมูลเพียงพอ','P7, P11–P12')]:
    box(s,x,1.94,3.45,3.5,PALE,radius=True);box(s,x,1.94,3.45,.13,BLUE)
    txt(s,title,x+.25,2.27,3.02,.7,20,NAVY,True)
    txt(s,body,x+.25,3.19,3.0,1.46,17,INK)
    txt(s,ref,x+.25,4.96,2.95,.25,12,TEAL,True)
txt(s,'ขอบเขตของข้อค้นพบ: เป็นผลการสังเคราะห์ภายในชุดบทความที่คัด ไม่ใช่การพิสูจน์ว่าทั่วโลกไม่มีงานอื่น',.8,5.83,11.7,.5,14,MUTED)
txt(s,'ที่มา: Husom et al. (2025), Giedra et al. (2026), Zheng et al. (2024), Sawalha & Al-Naymat (2025), Serepas et al. (2025)',.8,6.43,11.75,.25,10,MUTED)

# 7. Comparison retained from the original presentation.
s=base('จุดร่วมและความต่างของงานที่ทบทวน','ผลต่างด้านเครื่องและโจทย์ทำให้ย้ายตัวเลขจากบทความมาอ้างกับระบบบ้านไม่ได้ตรง ๆ')
box(s,.79,1.78,5.66,3.85,MINT,radius=True)
box(s,6.79,1.78,5.66,3.85,RGBColor(250,237,233),radius=True)
txt(s,'แนวโน้มร่วม',1.07,2.08,5.1,.42,22,NAVY,True)
txt(s,'ใช้การบีบอัดเพื่อลดภาระทรัพยากร\nให้ความสำคัญกับการประมวลผลใกล้ข้อมูล\nออกแบบชั้นเชื่อม IoT ให้ใช้ทรัพยากรต่ำ',1.07,2.81,5.0,2.15,18,INK)
txt(s,'ความต่างที่มีผลต่อการนำมาใช้',7.08,2.08,5.0,.43,22,NAVY,True)
txt(s,'อุปกรณ์ตั้งแต่ SBC ถึง GPU ระดับศูนย์ข้อมูล\nบางระบบเป็น hybrid บางระบบอยู่ในเครื่อง\nโจทย์และตัววัดไม่ตรงกับใบซื้อสินค้าไทย/อังกฤษ',7.08,2.81,4.98,2.17,18,INK)
txt(s,'จึงต้องทดสอบกับข้อมูลและ pipeline ของโครงงานเอง โดยรายงานผล PC และ NPU แยกกัน',.9,5.95,11.54,.59,19,NAVY,True)

# 8. Research question from the original, qualified.
s=base('ช่องว่างที่โครงงานจะศึกษา','งานที่ทบทวนมักรายงานผลของแต่ละชั้นแยกกัน',dark=True)
for x,head in [(.87,'โมเดล / ฮาร์ดแวร์'),(4.92,'JSON / ความถูกต้อง'),(8.97,'ระบบบ้าน / ปลายน้ำ')]:
    box(s,x,2.04,3.47,1.18,BLUE,radius=True);txt(s,head,x+.15,2.39,3.17,.43,19,WHITE,True,PP_ALIGN.CENTER)
txt(s,'คำถามวิจัย',.89,4.03,2.0,.42,19,RGBColor(255,211,123),True)
txt(s,'เมื่อนำขั้นตอนเหล่านี้มาต่อกันบนทรัพยากรจำกัด\nความผิดพลาดของข้อมูลกับต้นทุนประมวลผลเปลี่ยนอย่างไร?',.9,4.56,11.45,1.05,25,WHITE,True)
txt(s,'ผลนำร่อง e-Eye เป็นหลักฐานแรกของคำถามนี้ ยังไม่ใช่ผลครบทั้งระบบ',.9,6.18,11.5,.37,15,WHITE)

# 9. Overall pipeline, current vs planned.
s=base('สถาปัตยกรรมเชิงแนวคิดของโครงงาน','ภาพรวมสามชั้นจากรายงานทบทวนวรรณกรรม พร้อมสถานะปัจจุบัน')
for y,n,head,body,status,color in [(1.72,'1','รับรู้และสกัด','ภาพถ่ายก่อน; IP Camera ตามแผน → YOLO → OCR','มีผลนำร่องบน PC',BLUE),(3.19,'2','ประมวลผลในเครื่อง','Quantized Local LLM + grammar → JSON ที่ตรวจได้','อยู่ในแผนทดลอง',TEAL),(4.66,'3','ใช้งานปลายน้ำ','MQTT / Home Assistant → dashboard; burn rate เมื่อมีข้อมูลการใช้','อยู่ในแผนต่อยอด',NAVY)]:
    box(s,.79,y,.63,.94,color,radius=True);txt(s,n,.94,y+.23,.35,.44,23,WHITE,True,PP_ALIGN.CENTER)
    box(s,1.62,y,10.9,.95,PALE,radius=True)
    txt(s,head,1.85,y+.12,2.36,.34,19,NAVY,True)
    txt(s,body,4.02,y+.11,6.13,.65,17,INK)
    txt(s,status,10.32,y+.23,2.02,.37,13,color,True,PP_ALIGN.RIGHT)
txt(s,'ใบเสร็จบอกการซื้อเข้า; การคำนวณ burn rate ต้องมีข้อมูลคงเหลือหรือการใช้ตามเวลาเพิ่มเติม',.82,6.39,11.8,.38,14,MUTED)

# 10. Retain the original academic and architectural base, phrased for new listeners.
s=base('จากฐานวิชาการสู่ผลทดลอง','กรอบวรรณกรรม สถาปัตยกรรม และแผนเดิม นำมาสู่การทดลองนำร่องที่ตรวจได้')
for y,head,original,now in [
    (1.75,'งานวิจัย 3 มิติ','ฐานคิด: quantization / JSON / IoT','นำมาใช้: ตัวแปรและตัววัดการทดลอง'),
    (3.12,'สถาปัตยกรรม 3 ชั้น','ฐานคิด: กล้อง–YOLO–OCR–LLM–MQTT','นำมาใช้: e-Senses โดยเริ่มทดลอง e-Eye'),
    (4.49,'แผนดำเนินงาน','ฐานคิด: ต้นแบบ → LLM → IoT → pilot','ผลวันนี้: ภาพจริงและ YOLO/OCR บน PC'),
]:
    box(s,.8,y,11.72,1.08,PALE,radius=True)
    txt(s,head,1.05,y+.16,2.03,.68,18,NAVY,True)
    txt(s,original,3.1,y+.16,4.25,.68,16,INK)
    txt(s,now,7.5,y+.16,4.55,.68,16,BLUE,True)
txt(s,'ผลจาก PC ยังไม่ใช่ผล NPU หรือผลครบทั้งระบบ',.84,6.16,11.6,.47,19,ORANGE,True)

# 11. Show the relationship between all 59 reviewed images and the YOLO subsets.
s=base('ภาพ 59 ใบถูกใช้ทำอะไรบ้าง?','ตรวจข้อมูลภาพครบชุด แล้วแยกภาพตามความเหมาะสมของการทดลอง YOLO')
for x,n,head in [(.87,'124','ไฟล์ที่รับ'),(4.95,'113','ภาพ SHA-256 ไม่ซ้ำ'),(9.03,'59','ภาพผู้สมัครใบซื้อสินค้า')]:
    txt(s,n,x,1.91,3.28,.98,48,BLUE if n!='59' else TEAL,True)
    txt(s,head,x,2.91,3.25,.55,18,INK,True)
line(s,1.1,3.73,12.27,3.73,RGBColor(210,221,228),1.5)
for x,w,n,head,detail in [(.85,3.78,'48','ภาพชุดแรก','38 ฝึก + 10 ตรวจ'),(4.78,3.78,'6','ภาพฉากใหม่','ทดสอบโมเดลเดิม'),(8.71,3.78,'5','ภาพกันออก','หลายเอกสาร/เสี่ยงใกล้ซ้ำ')]:
    box(s,x,4.03,w,1.46,PALE,radius=True)
    txt(s,n,x+.17,4.2,.8,.57,30,BLUE if n!='5' else ORANGE,True)
    txt(s,head,x+1.05,4.14,w-1.22,.4,19,NAVY,True)
    txt(s,detail,x+1.05,4.7,w-1.23,.49,15,INK)
txt(s,'ตรวจข้อมูล/ทิศภาพครบ 59 ใบ; คะแนน YOLO หน้าถัดไปมาจากภาพตรวจ 10 + 6 ใบ ไม่ใช่คะแนนทั้ง 59 ใบ',.87,5.92,11.7,.55,17,NAVY,True)
txt(s,'59 ภาพยังไม่เท่ากับ 59 ธุรกรรมอิสระ',.88,6.48,11.2,.35,14,MUTED)

# 11. EDA figure from the real dataset.
s=base('ตรวจภาพใบซื้อสินค้า 59 ภาพครบชุด','ข้อมูลภาพและทิศตัวหนังสือครบทุกภาพ; การถอดชื่อสินค้ายังมีข้อจำกัด')
s.shapes.add_picture(str(EDA),Inches(.76),Inches(1.58),width=Inches(11.8),height=Inches(3.9))
txt(s,'พิมพ์ 41 / เขียนมือ 18  |  แนวตั้ง 38 / แนวนอน 21  |  ความสว่างมัธยฐานทั้งภาพ 173.9/255',.83,5.65,11.8,.46,18,NAVY,True)
txt(s,'ตรวจทั้ง 59 ภาพแล้ว: ชื่อสินค้าถอดครบ 12 | ถอดไม่ครบ 45 | ไม่มีบรรทัดชื่อ 2',.83,6.27,11.75,.38,16,NAVY,True)

# 13. Completed review of all 59 photos, with transcription limits clearly separated.
s=base('ตรวจภาพทั้ง 59 ใบแล้ว ได้ข้อมูลชื่อสินค้าแค่ไหน?','นับเฉพาะชื่อสินค้าบนบรรทัดรายการ; ตรวจด้วยตาครั้งแรกทุกภาพ')
for x,n,head,detail,color in [(.79,'12','ถอดชื่อครบ','ชื่อทุกบรรทัดที่เห็นอ่านได้',TEAL),(4.86,'45','ถอดไม่ครบ','28 ภาพอ่านได้บางช่วง; 17 ยังยืนยันไม่ได้',ORANGE),(8.93,'2','ไม่มีบรรทัดชื่อ','ไม่มีข้อความชื่อสินค้าให้ถอด',BLUE)]:
    box(s,x,1.9,3.59,3.34,PALE,radius=True)
    txt(s,n,x+.25,2.18,3.1,1.03,49,color,True)
    txt(s,head,x+.25,3.38,3.08,.51,22,NAVY,True)
    txt(s,detail,x+.25,4.05,3.06,.83,16,INK)
txt(s,'ใน 45 ภาพที่อ่านไม่ครบ มี 28 ภาพที่เก็บช่วงชื่อที่อ่านได้แน่ชัด และ 17 ภาพยังไม่มีช่วงชื่อที่ยืนยันได้',.88,5.55,11.63,.58,17,NAVY,True)
txt(s,'จึงยังไม่มีสัดส่วนภาษาไทย/อังกฤษที่แทนชื่อสินค้าในทั้ง 59 ภาพ; ยังไม่มีผู้ตรวจคนที่สอง',.88,6.26,11.55,.48,15,MUTED)

# 14. Explain the YOLO pilot without conflating its evaluation subsets with all 59 photos.
s=base('ผล YOLO: คะแนนนี้มาจากภาพตรวจ 16 ใบ','ใน 59 ภาพ ใช้ 38 ฝึกโมเดล / 10 ตรวจฉากเดิม / 6 ตรวจฉากใหม่ / กันออก 5')
box(s,.84,1.86,5.6,2.55,PALE,radius=True)
box(s,6.85,1.86,5.6,2.55,RGBColor(250,240,233),radius=True)
txt(s,'0.928',1.14,2.13,4.7,.91,44,TEAL,True)
txt(s,'10 ภาพฉากเดิม',1.16,3.33,4.82,.5,21,NAVY,True)
txt(s,'0.237',7.15,2.13,4.7,.91,44,ORANGE,True)
txt(s,'6 ภาพฉากใหม่',7.17,3.33,4.82,.5,21,NAVY,True)
txt(s,'mAP@0.5: คะแนนเฉลี่ยการหากรอบ 0–1; สูงดีกว่า',.93,4.72,11.5,.5,20,NAVY,True)
box(s,.86,5.43,11.6,.73,RGBColor(232,243,246),radius=True)
txt(s,'ลองหมุน 6 ภาพฉากใหม่ให้อ่านตรงด้วยโมเดลเดิม: 0.237 → 0.714',1.08,5.6,11.1,.37,18,BLUE,True)
txt(s,'ผลต่างเกี่ยวกับทิศภาพ แต่ฉากและแสงก็ต่างกัน; ยังสรุปความแม่นยำของทั้ง 59 ภาพไม่ได้',.91,6.44,11.5,.37,14,MUTED)

# 14. PC-side virtualisation and OCR.
s=base('การทดลองบน PC ก่อนมีบอร์ด','แยกผลที่วัดจริงออกจากความสามารถที่จะตรวจในระยะถัดไป')
box(s,.8,1.81,5.7,3.83,PALE,radius=True);box(s,6.79,1.81,5.7,3.83,RGBColor(232,243,246),radius=True)
txt(s,'EasyOCR ไทย / อังกฤษ',1.1,2.08,5.02,.45,22,NAVY,True)
txt(s,'ตรวจภาพพิมพ์ 3 ภาพ\nวันที่และยอดตรง 4 จาก 6 ช่อง\nเป็น spot-check โดยคนหนึ่งรอบ\nยังไม่ใช่ CER หรือผล JSON',1.1,2.74,5.05,2.33,19,INK)
txt(s,'RKNN Toolkit2 บน PC',7.09,2.08,5.04,.45,22,NAVY,True)
txt(s,'ONNX → RKNN เป้าหมาย RK3588\nรัน inference ผ่าน SDK บน PC ได้\nยังไม่ quantize และยังไม่มีค่า\nเวลา RAM หรือพลังงานบน NPU จริง',7.09,2.74,5.02,2.33,18,INK)
tag(s,'PC-side check ≠ NPU benchmark',3.83,6.0,5.67,ORANGE)

# 15. Selected, real receipt photo and its PC prediction from the reported model.
s=base('เดโมบน PC: จากภาพไปสู่กรอบเอกสาร','ตัวอย่างจริงจากชุดตรวจฉากเดิม แสดงภาพต้นฉบับคู่กับผล YOLOv8n')
txt(s,'ภาพต้นฉบับ',1.12,1.64,2.65,.35,17,NAVY,True,PP_ALIGN.CENTER)
txt(s,'ผลตรวจจับบน PC',4.23,1.64,2.65,.35,17,NAVY,True,PP_ALIGN.CENTER)
s.shapes.add_picture(str(DEMO_SOURCE),Inches(1.14),Inches(2.03),width=Inches(2.6),height=Inches(4.61))
s.shapes.add_picture(str(DEMO_RESULT),Inches(4.25),Inches(2.03),width=Inches(2.6),height=Inches(4.61))
txt(s,'→',3.79,4.0,.37,.45,25,TEAL,True,PP_ALIGN.CENTER)
box(s,7.38,2.03,5.07,4.61,PALE,radius=True)
txt(s,'สิ่งที่สาธิต',7.7,2.32,4.45,.48,22,NAVY,True)
txt(s,'โมเดลจากการฝึก 38 ภาพบน PC CPU\nภาพนี้อยู่ในชุดตรวจฉากเดิม 10 ภาพ\nแสดง 1 กรอบที่ confidence 0.981\nตั้งเกณฑ์แสดงผล confidence ≥ 0.80',7.7,3.02,4.27,2.35,17,INK)
txt(s,'ภาพตัวอย่างหนึ่งภาพ ไม่ใช่ผลทดสอบข้ามฉากหรือผลบน NPU',7.7,5.77,4.38,.64,15,ORANGE,True)

# 16. Roadmap, including conditional board phase.
s=base('งานถัดไปจากผลนำร่อง','ลำดับงานรักษาทิศทางของโครงงานทั้งระบบ')
for y,n,head,body in [(1.69,'1','แก้ชุดข้อมูล','ตรวจ label / ธุรกรรมซ้ำ และทำเฉลย OCR–JSON สองรอบ'),(2.75,'2','วัดแต่ละชั้น','เพิ่มฉากใหม่ เปรียบเทียบ OCR และทดสอบ LLM / JSON บน PC'),(3.81,'3','ตรวจการส่งออก','ทดสอบ quantization และ PC-side SDK โดยเก็บเวอร์ชันกับผล'),(4.87,'4','ต่อระบบและฮาร์ดแวร์','ทดสอบ MQTT ด้วยข้อมูลที่ตรวจแล้ว; ย้ายขึ้นบอร์ดเมื่อพร้อม')]:
    box(s,.92,y,.58,.58,BLUE,radius=True);txt(s,n,1.08,y+.1,.26,.27,16,WHITE,True,PP_ALIGN.CENTER)
    txt(s,head,1.76,y-.01,2.45,.5,20,NAVY,True)
    txt(s,body,4.18,y-.02,8.0,.7,17,INK)
txt(s,'อุปกรณ์เป้าหมายในระยะขอยืม: RK3588; จะวัด NPU จริงหลังได้รับบอร์ดและยืนยัน SDK',.94,6.16,11.5,.49,15,MUTED)

# 17. Close.
s=base('สรุปความก้าวหน้า','จากการทบทวนวรรณกรรมสู่หลักฐานทดลองนำร่อง',dark=True)
txt(s,'กรอบระบบ e-Senses และ pipeline สามชั้นยังเป็นเป้าหมายหลักของโครงงาน',.98,2.05,11.4,.74,24,WHITE,True)
txt(s,'วันนี้มีภาพจริง 59 ภาพผู้สมัคร และผล YOLO บน PC ที่ต่างกันระหว่างสองชุดภาพ\nจึงมีข้อมูลใช้วางการทดลอง OCR, JSON/LLM และฮาร์ดแวร์ขั้นถัดไป',.99,3.19,11.34,1.65,22,WHITE)
line(s,.98,5.52,5.14,5.52,TEAL,2)
txt(s,'ขอบคุณครับ  |  คำถามและข้อเสนอแนะ',.99,5.84,10.8,.62,24,WHITE,True)

prs.core_properties.title='ความก้าวหน้าโครงงานระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัย'
prs.core_properties.subject='การนำเสนอความก้าวหน้าโครงงานคอมพิวเตอร์'
prs.save(OUT)
print(OUT, len(prs.slides))
