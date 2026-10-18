import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/NATCHAPOL/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';

const root=process.cwd();
const work=path.join(process.env.USERPROFILE,'SeminarLab/preboard');
const out=path.join(work,'document_review/revision');
await fs.mkdir(out,{recursive:true});
const read=async file=>JSON.parse(await fs.readFile(path.join(root,'reports/preboard',file),'utf8'));
const ocr=await read('single_pass_ocr.json'), llm=await read('single_pass_llm.json'), pc=await read('pc_transport_profile.json');
if(process.argv.includes('--final')&&(!llm.complete||pc.run_id!=='pc-delivery-profile-engineering-v3'||pc.failures))throw Error('Final release requires completed LLM matrix and corrected-parser PC profile');
const source=path.join(root,'ass5_output/Residential_Intelligence_Project_Progress_READY_2026-10-18.pptx');
const deck=await PresentationFile.importPptx(await FileBlob.load(source));
const inspection=await deck.inspect({kind:'slide,textbox,shape,image',maxChars:300000});
const records=inspection.records;
const originalSlides=[...deck.slides.items];
const changes=[];
function set(id,text,fontSize){
 const record=records.find(r=>r.id===id); if(!record)throw Error('Unknown source '+id);
 const target=deck.resolve(id);target.text=text;
 target.text.style={...record.style,...(fontSize?{fontSize}:{}),typeface:'Tahoma'};
 changes.push({id,before:record.text,after:text});
}
const fmt=v=>(v*100).toFixed(2)+'%';
const introFlow=records.find(r=>r.kind==='textbox'&&r.slideIndex===1&&r.text?.startsWith('แนวทางเดิมยังอยู่'));
if(introFlow)set(introFlow.id,'รับภาพ → YOLO/OCR → Local LLM/JSON → MQTT/Home Assistant',28);
set('sh/xcz2l03q','อุปกรณ์ตั้งแต่ SBC ถึง GPU ระดับศูนย์ข้อมูล\nบางระบบเป็น hybrid บางระบบอยู่ในเครื่อง\nโจทย์และตัววัดต่างจากใบซื้อสินค้าของเรา',24);
set('sh/tcfel0vu','ใน 12 ฉบับ มีงานในกรอบสามมิติ 11 ฉบับ และงานสนับสนุนข้ามศาสตร์ 1 ฉบับ',21.33);
const oldExternal=records.find(r=>r.kind==='textbox'&&r.slideIndex===10&&r.text==='ภาพฉากใหม่');
if(oldExternal)set(oldExternal.id,'ภาพส่งเพิ่มเดิม',25);
for(const r of records.filter(r=>r.kind==='textbox')){
 if(r.slideIndex===11&&r.text?.startsWith('ตรวจทั้ง 59 ภาพแล้ว'))set(r.id,'ผลตรวจชื่อสินค้าเดิม: ถอดครบ 12 / ไม่ครบ 45 / ไม่มีบรรทัดชื่อ 2 ภาพ',23);
 if(r.slideIndex===11&&r.text?.startsWith('ข้อมูลภาพและทิศตัวหนังสือ'))set(r.id,'ตรวจข้อมูลภาพครบทุกภาพ ข้อความอ้างอิงรอบล่าสุดแสดงในหน้าถัดไป',20);
 if(r.slideIndex===13&&r.text?.includes('ฉากใหม่'))set(r.id,r.text.replaceAll('ฉากใหม่','ส่งเพิ่มเดิม'));
 if(r.slideIndex===13&&r.text?.startsWith('ใน 59 ภาพ ใช้'))set(r.id,'ฝึก 38 ภาพ / ตรวจฉากเดิม 10 / ตรวจภาพส่งเพิ่ม 6 / กันออก 5',21.33);
 if(r.slideIndex===16&&r.text==='ต่อระบบและฮาร์ดแวร์')set(r.id,'ระบบและ\nฮาร์ดแวร์',23);
}
set('sh/i94r6xgz','ภาพและข้อความอ้างอิงหนึ่งรอบ\nYOLO และ OCR บน PC\nLocal LLM สร้าง JSON\nเดโม MQTT / Home Assistant',25.33);
set('sh/w72947yt','ยังไม่มีคะแนนเนื้อหา JSON / NPU');
const objective=records.find(r=>r.kind==='textbox'&&r.slideIndex===3&&r.text?.startsWith('1  ออกแบบ'));
if(objective)set(objective.id,'1  ออกแบบ e-Senses และกระบวนการในบ้าน\n2  สกัดภาพใบซื้อสินค้าเป็น JSON ที่ตรวจได้\n3  วัดความถูกต้อง เวลา และทรัพยากรบน PC\n4  ส่งข้อมูลเข้าระบบบ้าน และต่อยอดการวิเคราะห์',24);
set('sh/qlcjipgn','ประมวลผล\nในเครื่อง',23);
set('sh/0ru1ozyp','มีผลรูปแบบ JSON',18.5);
set('sh/hcji5o7a','เชื่อมเดโมบน PC',18.5);
set('sh/cbu58j2h','ตัวอย่างข้อมูลสมมติเพื่ออธิบายหน้าตาระบบ ผลรันจริงอยู่ในช่วงเดโม',21.33);
set('sh/103qxcbq','ต้นแบบมีขั้นตรวจยืนยันแล้ว การวิเคราะห์อัตราการใช้ยังต้องมีข้อมูลคงเหลือ',17.33);
set('sh/q50nydsj','ข้อมูล 59 ภาพ และข้อความอ้างอิงที่บันทึกแล้ว',34.66);
set('sh/bq9orito','ตรวจข้อความหนึ่งรอบ จำนวนภาพที่ใช้แต่ละคะแนนระบุแยกตามเกณฑ์',21.33);
set('sh/gzy5s3a1',String(ocr.candidate_photos));set('sh/1076lobm','ภาพที่รวบรวม');
set('sh/hcfy9k3u','ตรวจข้อมูลภาพแล้ว\nยังไม่เท่ากับธุรกรรมอิสระ',21.33);
set('sh/vaxg7ulo',String(ocr.saved_photos));set('sh/u9ofyp43','มีข้อความบันทึก');
set('sh/t8fy5k3i','ผู้บันทึกหนึ่งคน หนึ่งรอบ\nเก็บส่วนอ่านไม่ครบตามจริง',21.33);
set('sh/7mdg3als',String(ocr.scorable_photos));set('sh/6l4fu547','ใช้เทียบ CER');
set('sh/lkvy103m','ผ่านเกณฑ์คัดข้อความ\nยังไม่รับรองว่าครบทุกตัว',21.33);
set('sh/kjmxsfm1',`${ocr.excluded_photos} ภาพมีข้อความไม่ครบหรือจัดรูปแบบใหม่ จึงไม่นับใน CER เต็มข้อความ`,23);
set('sh/cnqh8fux',ocr.missing_doc_ids.length?`${ocr.missing_doc_ids.length} ภาพยังไม่มีข้อความบันทึก เฉลย JSON และกลุ่มธุรกรรมยังไม่รับรองครบ`:'บันทึกข้อความครบ 59 ภาพแล้ว เฉลย JSON และกลุ่มธุรกรรมยังไม่รับรองครบ',20);
set('sh/547mhg3m','OCR ยังผิดพลาดสูงเมื่อเทียบข้อความหนึ่งรอบ',34.66);
set('sh/k3y5ov21',`เปรียบเทียบพิกเซลภาพเดียวกัน ${ocr.scorable_photos} ภาพ รวม ${ocr.summaries.all_eligible.easyocr.reference_characters.toLocaleString('en-US')} ตัวอักษรอ้างอิง`,21.33);
set('sh/m9c3e1kn','EasyOCR ไทย / อังกฤษ');
set('sh/wrm9kvep',`micro CER ${fmt(ocr.summaries.all_eligible.easyocr.micro_cer)}\nค่า CER ต่ำ หมายถึงผิดน้อย\nตัวหารเป็นตัวอักษรอ้างอิง\nยังมีข้อผิดพลาดจากภาพและเฉลย`,25.33);
set('sh/hsvat0fa','Tesseract ไทย / อังกฤษ');
set('sh/upkrilwj',`micro CER ${fmt(ocr.summaries.all_eligible.tesseract.micro_cer)}\nใช้ตัวอ่านผล TSV ที่แก้แล้ว\nรัน OCR ใหม่ครบ 59 ภาพ\nคิด CER เฉพาะภาพผ่านเกณฑ์`,25.33);
set('sh/4vm9ovel','ผลเชิงพรรณนา ไม่ใช่คะแนนชุดทดสอบอิสระ',17.33);
set('sh/4by9or6l','รับรองกรอบและกลุ่มธุรกรรม พร้อมเฉลย JSON สำหรับคะแนนเนื้อหา',25.33);
set('sh/gnepkr69','เก็บภาพต่างฉากใหม่ แยกจากชุดพัฒนา แล้ววัดครบกระบวนการ',25.33);
set('sh/0ji9wb6t','คงผล RKNN บน PC และตรวจ SDK ก่อนทดลองบนอุปกรณ์จริง',25.33);
set('sh/ny5876xc','เดโม MQTT เชื่อมได้แล้ว เพิ่มการประเมินกับผู้ใช้เมื่อพร้อม',25.33);
set('sh/6hw3y9sb',`ชุดภาพ 59 ภาพ มีข้อความหนึ่งรอบ ${ocr.saved_photos} ภาพ\nมีผล OCR, รูปแบบ JSON และเดโม PC ถึง Home Assistant\nเนื้อหา JSON / ภาพต่างฉากใหม่: ยังไม่ได้ทดลอง`,28);
set('sh/fapkr6pw','ขอบคุณผู้ฟังครับ   Q&A');

const navy='#1D2A5D',ink='#1D2F3E',muted='#5A7180',pale='#E6F2F5';
function text(slide,value,left,top,width,height,size=26,bold=false,color=ink){
 const s=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 s.text=value;s.text.style={typeface:'Tahoma',fontSize:size,bold,color,alignment:'left'};s.text.insets=0;return s;
}
function slide(title,subtitle){
 const s=deck.slides.add({background:{fill:'#FFFFFF'}});
 text(s,title,65.28,40.32,1152,59.52,35.5,true,navy);
 text(s,subtitle,67.2,107.52,1142.4,55,21.33,false,muted);
 return s;
}
function table(s,values,widths,top=205,height=300){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:76,top,width:1128,height,columnWidths:widths,values});
 t.borders.assign({fill:'#C7D5DD',width:1,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?navy:r%2?pale:'#FFFFFF';
  cell.text.style={typeface:'Tahoma',fontSize:r===0?21:23,bold:r===0,color:r===0?'#FFFFFF':ink,alignment:c===0?'left':'center'};
 }
 return t;
}
const s17=slide('ผล Local LLM ด้านรูปแบบ JSON','Qwen3 สองขนาด สองระดับ quantization เปิดและปิด grammar');
const values=[['โมเดล','ข้อความผู้บันทึก\nปิด grammar','ข้อความผู้บันทึก\nเปิด grammar','ข้อความ OCR\nปิด grammar','ข้อความ OCR\nเปิด grammar']];
for(const model of ['qwen3-0.6B-Q8_0','qwen3-0.6B-Q4_K_M','qwen3-1.7B-Q8_0','qwen3-1.7B-Q4_K_M']){
 const row=[model.replace('qwen3-','')];
 for(const source of ['owner_text','tesseract'])for(const grammar of [false,true]){
  const g=llm.groups.find(g=>g.model===model&&g.source===source&&g.grammar===grammar);
  row.push(g?`${g.schema_valid}/${g.attempts}`:'ยังไม่รัน');
 }values.push(row);
}
table(s17,values,[240,222,222,222,222],195,305);
text(s17,`ในตาราง: ผ่าน schema / รันจริง   บันทึกแล้ว ${llm.attempts}/${llm.expected_attempts} ครั้ง`,80,525,1120,42,23);
text(s17,'Q4_K_M แปลงต่อจาก Q8_0 จึงยังไม่แยกผล quantization จากฐาน BF16',80,578,1120,35,21);
text(s17,'ตรวจว่าคำตอบจบครบและตรง schema ก่อนใช้งาน\nความถูกต้องของชื่อสินค้าและยอดเงินยังไม่ได้ทดลอง',80,613,1120,54,21,true,navy);

const s18=slide('เดโมภาพจริงส่งข้อมูลถึง Home Assistant ได้แล้ว','ตรวจค่าปลายทางกับ JSON ที่ส่ง ภายในสภาพแวดล้อมทดลองบน PC');
const stages=['ภาพจริง\nตรวจกรอบ','OCR\nอ่านข้อความ','Local LLM\nสร้าง JSON','ตรวจยืนยัน\nก่อนส่ง','MQTT\nHome Assistant'];
for(let i=0;i<5;i++){
 const x=78+i*230;
 const box=s18.shapes.add({geometry:'roundRect',position:{left:x,top:185,width:207,height:95},fill:pale,line:{fill:'#CCDDE4',width:1}});
 text(s18,stages[i],x+12,202,183,75,i===4?20:24,true,navy);
 if(i<4)text(s18,'→',x+208,214,25,40,27);
}
const deliveries=[['ภาพจริง','ยอดรวมที่ HA รับ','จำนวนรายการที่ HA รับ']];
for(const id of [...new Set(pc.traces.map(t=>t.doc_id))]){
 const raw=JSON.parse(await fs.readFile(path.join(work,'runs',pc.run_id,`${id}-r0.json`),'utf8'));
 const states=raw.ha_states||[];
 deliveries.push([id,states.find(x=>x.entity_id==='sensor.seminar_latest_purchase_total')?.state||'ไม่มีค่า',states.find(x=>x.entity_id==='sensor.seminar_latest_item_count')?.state||'ไม่มีค่า']);
}
table(s18,deliveries,[440,344,344],330,205);
text(s18,'ตรวจ event_id และค่าทั้งสองปลายทาง รวมกรณีส่งซ้ำและ broker หยุด',80,560,1120,35,23);
text(s18,'ค่าที่แสดงมาจากโมเดล ยังไม่ได้ทดลองความถูกต้องของเนื้อหา\nชุดทดสอบใช้การยืนยันอัตโนมัติเพื่อวัดการส่งข้อมูล',80,604,1120,65,21,true,navy);

const pcConfig=pc.configuration;
const pcSubtitle=pcConfig?`${pcConfig.model_id.replace('qwen3-','Qwen3 ')} กับ ${pcConfig.engine}, 3 ภาพ × 3 รอบ แยก warm-up`:'3 ภาพ รันซ้ำภาพละ 3 รอบ โหลดโมเดลค้างไว้และแยก warm-up';
const s19=slide('เวลาและหน่วยความจำของเดโมบน PC',pcSubtitle);
const stats=pc.summaries;
const metricRows=[['ตัวชี้วัด','มัธยฐาน','ต่ำสุด–สูงสุด']];
for(const [key,label,scale,unit] of [['automated_window_to_ha_observed_seconds','ภาพถึงสังเกตค่าใน HA',1,'วินาที'],['publish_to_ha_observed_seconds','เริ่มส่งถึงสังเกตค่าใน HA',1,'วินาที'],['windows_full_host_rss_bytes','RSS ฝั่ง Windows host',2**30,'GiB']]){
 const v=stats[key];metricRows.push([label,`${(v.median/scale).toFixed(3)} ${unit}`,`${(v.min/scale).toFixed(3)}–${(v.max/scale).toFixed(3)}`]);
}
table(s19,metricRows,[540,294,294],185,250);
text(s19,'เวลาเต็มกระบวนการยังไม่รวมเวลาที่มนุษย์ตรวจแก้\nRSS ของ Home Assistant และ broker วัดแยกใน Linux',80,467,1120,85,25);
text(s19,'RKNN แปลงและรันผ่าน SDK บน PC ได้แล้ว\nผล NPU, RAM และพลังงานบน RK3588 ยังต้องรอบอร์ด',80,575,1120,75,25,true,navy);
const slideIds=(await deck.inspect({kind:'slide',maxChars:40000})).records.filter(r=>r.kind==='slide').map(r=>r.id);
deck.slides.reorder([...slideIds.slice(0,16),...slideIds.slice(18,21),...slideIds.slice(16,18)]);
// Match the retained footer and renumber every page after insertion.
for(let i=0;i<deck.slides.items.length;i++){
 const s=deck.slides.items[i];
 if([s17,s18,s19].includes(s)){
  s.shapes.add({geometry:'rect',position:{left:67.2,top:676,width:1148,height:1.4},fill:'#D4DFE5',line:{fill:'none',width:0}});
  text(s,'โครงงานคอมพิวเตอร์ | รายงานความก้าวหน้า | 18 ต.ค. 2569',69.12,681.6,960,21.12,11.3,false,muted);
  text(s,String(i+1),1176,681.6,33.6,21.12,11.3,false,muted);
 }else{
  const oldIndex=originalSlides.indexOf(s);
  const footer=records.find(r=>r.kind==='textbox'&&r.slideIndex===oldIndex&&r.position.left>1150&&r.position.top>670);
  if(footer)set(footer.id,String(i+1));
 }
}
// Retain old speaking explanations for unchanged slides, and replace changed sections.
const oldScript=(await fs.readFile(path.join(root,'ass5_output/Residential_Intelligence_Presentation_Script_2026-10-18.md'),'utf8')).replace(/\r\n?/g,'\n');
const oldParts=[...oldScript.matchAll(/^(\d+)\. \*\*(.*?)\*\*[^\n]*$/gm)].map(m=>({number:Number(m[1]),text:m[0].replace(/^\d+\. /,'')}));
const notes=Array(21).fill('');
for(let i=0;i<16;i++)notes[i]=oldParts.find(p=>p.number===i+1)?.text||'';
notes[0]='**ชื่อโครงงาน** — สวัสดีครับ ผมนายณัชพล เพ็งพล และนายธนบดี เริ่มรักสกุล นำเสนอโครงงานหมายเลข SCS3-4 กลุ่มสอบ SCS3 อาจารย์ที่ปรึกษาคือ ผศ.บุญทรัพย์ ไวคำ โครงงานศึกษาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัย โดยเริ่มจากภาพใบซื้อสินค้าและแปลงเป็นข้อมูลที่ตรวจสอบและใช้ต่อได้ วันนี้จะเริ่มจากกรอบระบบและฐานวิชาการเดิม แล้วนำเสนอผลทดลองเพิ่มเติมบน PC';
notes[3]='**วัตถุประสงค์และขอบเขต** — เป้าหมายยังเป็นระบบ e-Senses และกระบวนการสามชั้นจากฐานเดิม วันนี้มีผลตรวจภาพ ข้อความหนึ่งรอบ OCR การสร้าง JSON และเดโมถึง Home Assistant แล้ว แต่คะแนนความถูกต้องเนื้อหา JSON และผลบน NPU ยังไม่มี การผ่านรูปแบบและการส่งสำเร็จจึงเป็นความก้าวหน้าคนละส่วนกับความแม่นยำของข้อมูล';
notes[4]+=' ตัวเลขนี้เป็นประวัติการคัดกรองในบัญชีเดิม ข้อสงวนหนึ่งรายการหมายถึง A Survey on LLM Edge-Intelligence: Recent Advances and Open Challenges ซึ่งบัญชีเดิมให้ใช้เฉพาะการอภิปรายและงานอนาคต ไม่ใช้เป็นหลักฐานหลัก รายการนี้ไม่ใช่หนึ่งใน 12 ฉบับที่นำมาสังเคราะห์ในรายงาน';
notes[4]=notes[4].replace('57 รายการที่ติดแท็ก Ring0','57 รายการในกลุ่มที่เกี่ยวข้องโดยตรง').replace('ส่วน P5 อยู่ภายใน 12 ฉบับนี้เพื่อสนับสนุนแนวคิดข้ามศาสตร์','ส่วนงานอุปกรณ์สวมใส่ทางการแพทย์เป็นหนึ่งใน 12 ฉบับนี้และใช้สนับสนุนแนวคิดข้ามศาสตร์');
notes[5]+=' รหัส P1 ถึง P12 ที่ใต้กลุ่มเป็นลำดับบทความในรายงานทบทวนวรรณกรรมเดิม ส่วน P5 เป็นงานสนับสนุนข้ามศาสตร์ที่กล่าวในหน้าก่อน';
notes[8]='**สถาปัตยกรรมสามชั้น** — ชั้นแรกตรวจกรอบและอ่านข้อความจากภาพ ชั้นที่สองให้โมเดลภาษาในเครื่องสร้าง JSON แล้วตรวจ schema ชั้นสุดท้ายให้ผู้ใช้ตรวจยืนยันและส่งข้อมูลซื้อเข้าสู่ Home Assistant ทั้งสามชั้นมีต้นแบบเชื่อมกันบน PC แล้ว การคำนวณอัตราการใช้ยังต้องมีข้อมูลคงเหลือเพิ่มเติม';
notes[9]='**หน้าตาระบบ** — ตัวอย่างร้าน ข้าว และนมในหน้านี้เป็นข้อมูลสมมติสำหรับอธิบายสิ่งที่ผู้ใช้จะเห็น ระบบต้องแสดงรายการที่ตรวจแก้ได้ก่อนส่งเข้าบ้านอัจฉริยะ ต่อไปจะเห็นผลจากภาพจริงในช่วงเดโม จึงไม่ควรนำยอด 150 บาทในตัวอย่างนี้ไปอ้างเป็นผลทดสอบ';
notes[10]=notes[10].replaceAll('ภาพฉากใหม่','ภาพส่งเพิ่มเดิม')+' ภาพส่งเพิ่มเดิมหกภาพนี้เป็นหลักฐานย้อนหลัง ส่วนชุดภาพต่างฉากใหม่สำหรับการทดสอบสุดท้ายยังไม่ได้ทดลอง';
notes[11]='**ข้อมูลภาพครบชุด** — ใน 59 ภาพ มีเอกสารพิมพ์ 41 ภาพและเขียนมือ 18 ภาพ รูปภาพเป็นแนวตั้ง 38 และแนวนอน 21 ซึ่งนับจากรูปทรงภาพ ไม่ใช่ทิศตัวอักษร ค่าความสว่างมัธยฐาน 173.9 จาก 255 คำนวณทั้งภาพรวมพื้นหลัง จึงไม่ได้บอกความแม่นยำ OCR โดยตรง ผลชื่อสินค้า 12 ภาพครบ 45 ภาพไม่ครบและสองภาพไม่มีบรรทัดชื่อสินค้าเป็นการตรวจเดิม ข้อความทุกบรรทัดที่ผู้จัดทำบันทึกรอบล่าสุดครบ 59 ภาพแสดงหน้าถัดไป';
notes[13]=notes[13].replaceAll('ฉากใหม่','ส่งเพิ่มเดิม').replace('หกภาพใหม่นี้','ภาพส่งเพิ่มหกภาพนี้');
notes[12]=`**จำนวนภาพและข้อความอ้างอิง** — รวบรวมไว้ 59 ภาพ และมีข้อความจากการตรวจหนึ่งรอบ ${ocr.saved_photos} ภาพ ข้อความบางภาพอ่านได้ไม่ครบหรือจัดเป็นตารางใหม่ จึงเก็บไว้ทั้งหมด แต่ใช้เทียบ CER เต็มข้อความเฉพาะ ${ocr.scorable_photos} ภาพตามเกณฑ์ที่ประกาศ อีก ${ocr.excluded_photos} ภาพไม่รวมในคะแนนนี้ และ ${ocr.missing_doc_ids.length} ภาพยังไม่มีข้อความ จำนวนภาพยังไม่ใช่จำนวนธุรกรรมอิสระ ผลเก่าที่กล่าวถึงชื่อสินค้าครบ 12 ภาพเป็นการตรวจอีกขอบเขตหนึ่ง`;
notes[14]=`**ผล OCR** — CER คืออัตราความผิดพลาดตัวอักษร ซึ่งต่ำกว่าหมายถึงผิดน้อย ในชุด ${ocr.scorable_photos} ภาพ EasyOCR ได้ ${fmt(ocr.summaries.all_eligible.easyocr.micro_cer)} และ Tesseract ${fmt(ocr.summaries.all_eligible.tesseract.micro_cer)} ตัวเลขนี้ไม่ใช่เปอร์เซ็นต์ความแม่นยำ ทั้งคู่ยังผิดพลาดสูง และข้อความอ้างอิงตรวจเพียงหนึ่งรอบ ผลนี้จึงช่วยระบุปัญหา แต่ยังไม่พิสูจน์ประสิทธิภาพทั่วไป Tesseract ใช้ผลรันใหม่หลังแก้การอ่านไฟล์ TSV แล้ว`;
notes[15]=notes[15].replace('และยังไม่ใช่ระบบ OCR→JSON ครบวงจร','เดโมในหน้านี้แสดงเฉพาะขั้นตรวจกรอบ ส่วนเดโมครบกระบวนการถึง Home Assistant อยู่ในสไลด์ 18');
notes[16]=`**Local LLM และ schema** — ตารางแสดงจำนวนครั้งที่ JSON ตรง schema ต่อจำนวนครั้งที่รันจริง ใช้ภาพเดิม 6 ภาพ ข้อความสองแหล่ง โมเดลสองขนาด สองระดับบีบอัด และเปิดปิด grammar รันซ้ำสามรอบ รวมแผน 288 ครั้ง ขณะสร้างไฟล์นี้มี ${llm.attempts} ครั้ง การรันซ้ำใช้วัดเวลา ไม่เพิ่มจำนวนภาพ ข้อควรระวังคือ null หรือรายการว่างอาจผ่าน schema ได้ เราจึงยังไม่อ้างความถูกต้องชื่อสินค้าและยอดเงิน และ Q4 แปลงต่อจาก Q8 ไม่ได้เริ่มจาก BF16`;
notes[17]='**เดโมครบกระบวนการ** — เปิดเดโมที่ http://127.0.0.1:8090/demo และใช้รายการผลรันที่เตรียมไว้ แสดงภาพต้นฉบับ กรอบ ข้อความ OCR และ JSON ก่อนดูสถานะส่งและค่าใน Home Assistant ตารางนี้เป็นค่าที่ระบบรับจริงจากสามภาพ แต่ยังไม่ใช่เฉลยที่รับรองว่ารายการถูกทุกช่อง ชุดทดสอบใช้การยืนยันอัตโนมัติแทนมนุษย์เพื่อวัดทางเทคนิค และมีการตรวจการส่งซ้ำกับกรณี broker หยุด หากเดโมสดไม่พร้อมให้ใช้หลักฐานผลรันนี้โดยบอกว่าเป็นผลบันทึก';
notes[18]='**เวลาและ RAM** — ตารางวัดจากสามภาพภาพละสามรอบ โดยโหลดโมเดลค้างในหน่วยความจำ เวลาเต็มทางใช้การยืนยันอัตโนมัติ จึงยังไม่รวมเวลาที่ผู้ใช้ตรวจแก้ เวลาสังเกตค่า Home Assistant มี HTTP polling รวมอยู่ ส่วนหน่วยความจำเป็น RSS ของกระบวนการตามขอบเขตที่ระบุ ไม่ใช่ RAM ทั้งเครื่อง งานแปลง RKNN บน PC มีแล้ว แต่การวัด NPU และพลังงานจริงต้องรอบอร์ด';
notes[18]+=` รอบนี้มัธยฐานจากภาพถึงสังเกตค่า HA คือ ${pc.summaries.automated_window_to_ha_observed_seconds.median.toFixed(3)} วินาที และ RSS ฝั่ง Windows host มีมัธยฐาน ${(pc.summaries.windows_full_host_rss_bytes.median/2**30).toFixed(3)} GiB`;
if(pcConfig)notes[18]+=` ชุดวัดนี้ใช้ ${pcConfig.model_id} กับ ${pcConfig.engine} และ ${pcConfig.grammar?'เปิด':'ปิด'} grammar ทิศภาพอาศัยข้อมูลที่ผู้จัดทำเลือกไว้ ยังไม่ใช่ระบบหมุนภาพอัตโนมัติ`;
notes[19]='**งานที่ยังค้าง** — ส่วนที่ยังทำต่อก่อนมีบอร์ดได้คือรับรองกรอบและธุรกรรมซ้ำ ทำเฉลย JSON สำหรับคะแนนเนื้อหา และเก็บภาพต่างฉากใหม่ที่ไม่ปะปนชุดพัฒนา จากนั้นจึงสรุปความถูกต้องครบกระบวนการ งานเหล่านี้ยังค้างจริง ส่วนการวัดบน RK3588 จะเริ่มเมื่อมีบอร์ดและ runtime พร้อม';
notes[20]=`**สรุปและ Q&A** — โครงงานยังยึดกรอบ e-Senses และฐานวรรณกรรมเดิม วันนี้มีภาพ 59 ภาพ ข้อความหนึ่งรอบ ${ocr.saved_photos} ภาพ และหลักฐาน OCR รูปแบบ JSON กับเดโมถึง Home Assistant ข้อจำกัดที่ยังต้องทำต่อคือคะแนนเนื้อหา JSON ภาพต่างฉากใหม่ และผลฮาร์ดแวร์ ขอบคุณผู้ฟังครับ ยินดีรับคำถามและข้อเสนอแนะ`;
notes[12]=notes[12].replace(' และ 0 ภาพยังไม่มีข้อความ',' บันทึกครบทั้งชุดแล้ว');
notes[14]+=' ก่อนคำนวณตัดเฉพาะป้ายอ้างอิง [cite: N] ซึ่งไม่ใช่ข้อความในภาพ แล้วปรับ Unicode และช่องว่างตามวิธีเดียวกันทั้งสองเครื่องมือ โดยเก็บข้อความดิบไว้';
notes[16]+=' หกภาพถูกเลือกตามความยาวข้อความจาก checkpoint ที่บันทึก 55 ภาพก่อนดูผลโมเดล และตรึงข้อความไว้ การเติมสี่ภาพท้ายทำให้ชุดข้อความรวมครบ 59 ภาพ แต่ไม่ได้เปลี่ยนชุดย่อย LLM ให้เป็นตัวแทนแบบสุ่มของทั้งชุด';
try {
 const audit=await read('completed_run_audit.json');
 notes[16]+=` ผลตรวจคำตอบดิบพบการถูกตัดที่เพดาน 2,048 tokens ${audit.llm_status_counts.truncated||0} ครั้ง ในจำนวนนี้เปิด grammar ${audit.grammar_truncated} ครั้ง การบังคับรูปแบบจึงยังต้องตรวจว่าคำตอบจบครบก่อนใช้งาน ทุกครั้งยังรวมอยู่ในตัวหาร`;
} catch(error) {if(process.argv.includes('--final'))throw error;}
const literatureSources={
  4:'รายงาน Ass4 และบันทึกการคัดกรองวรรณกรรมของโครงงาน จำนวนที่คัดกรองเป็นผลของผู้จัดทำ',
  5:'Husom et al. https://doi.org/10.1145/3767742; Giedra et al. https://www.mdpi.com/2079-9292/15/11/2451; SGLang https://proceedings.neurips.cc/paper_files/paper/2024/hash/724be4472168f31ba1c9ac630f15dec8-Abstract-Conference.html; Sawalha et al. https://www.mdpi.com/2624-831X/6/3/39; Serepas et al. https://www.mdpi.com/2073-431X/14/9/391',
  6:'ShadowNPU https://arxiv.org/abs/2508.16703; Hybe https://pure.kaist.ac.kr/en/publications/hybe-gpu-npu-hybrid-system-for-efficient-llm-inference-with-milli/; EdgeLLM https://doi.org/10.1109/ICWS62655.2024.00099',
  7:'DocOwl2 https://aclanthology.org/2025.acl-long.291/; SGLang https://proceedings.neurips.cc/paper_files/paper/2024/hash/724be4472168f31ba1c9ac630f15dec8-Abstract-Conference.html; Zheng et al. https://arxiv.org/abs/2410.11845'
};
for(let i=0;i<notes.length;i++)deck.slides.items[i].speakerNotes.text=notes[i]+'\nหลักฐาน: '+(literatureSources[i]||'reports/preboard/single_pass_ocr.json; single_pass_llm.json; pc_transport_profile.json; ass5_ready_evidence.md');
await fs.writeFile(path.join(out,'Ass5_Script_DRAFT.md'),'# บทพูดประกอบสไลด์ความก้าวหน้า\n\n21 สไลด์ ใช้ประกอบ Ass5 ฉบับปรับผลทดลอง เวลาโดยประมาณ 16–20 นาทีรวมเดโม\n\n'+notes.map((t,i)=>`${i+1}. ${t}`).join('\n\n')+'\n','utf8');
await fs.writeFile(path.join(out,'ass5_changes.json'),JSON.stringify(changes,null,2));
await (await PresentationFile.exportPptx(deck)).save(path.join(out,'Ass5_DRAFT.pptx'));
for(let i=0;i<deck.slides.items.length;i++){
 const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log('Exported 21 slides and matching script',out);
process.exit(0);
