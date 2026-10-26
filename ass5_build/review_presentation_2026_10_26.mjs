import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/NATCHAPOL/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=process.cwd(), dir=path.join(root,'.codex-finalizer/review-2026-10-26');
await fs.mkdir(dir,{recursive:true});
const source=path.join(root,'DEMO_PRESENTATION_2026-10-21/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pptx');
const deck=await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot=await deck.inspect({kind:'slide,textbox,shape,table,notes',maxChars:400000});
await fs.writeFile(path.join(dir,'inspection.json'),JSON.stringify(snapshot.records,null,2));
if(process.argv.includes('--inspect')){console.log('Imported',deck.slides.items.length,'slides; inspection saved');process.exit(0);}
const replacements=[
 ['ตรวจข้อมูล/ทิศภาพครบ 59 ใบ; คะแนน YOLO หน้าถัดไปมาจากภาพตรวจ 10 + 6 ใบ ไม่ใช่คะแนนทั้ง 59 ใบ','ตรวจข้อมูล/ทิศภาพครบ 59 ใบ; ผล YOLO สไลด์ 14 ใช้ภาพตรวจ 10 + 6 ใบ ไม่ใช่ทั้ง 59 ใบ'],
 ['ตรวจค่าปลายทางกับ JSON ที่ส่ง ภายในสภาพแวดล้อมทดลองบน PC','ผลทดสอบการส่งข้อมูลบน PC ก่อนมนุษย์ตรวจแก้; คลิปแสดงขั้นตรวจแก้จริง'],
 ['ค่าที่แสดงมาจากโมเดล ยังไม่ได้ทดลองความถูกต้องของเนื้อหา','ค่าดิบจากโมเดลอาจผิด: ตารางนี้ยืนยันการส่ง ไม่ใช่ความถูกต้องของยอดซื้อ'],
 ['Qwen3 0.6B-Q4_K_M กับ tesseract, 3 ภาพ × 3 รอบ แยก warm-up','Qwen3 0.6B-Q4_K_M / Tesseract: 3 ภาพ × 3 รอบ แยก warm-up'],
 ['เวลาเต็มกระบวนการยังไม่รวมเวลาที่มนุษย์ตรวจแก้','คงโมเดลในหน่วยความจำ / ยืนยันอัตโนมัติ / ไม่รวมเวลาคนตรวจแก้'],
];
for(const [before,after] of replacements){
 const record=snapshot.records.find(r=>r.kind==='textbox'&&r.text?.includes(before));
 if(!record)throw Error('Missing anchor: '+before);
 const slide=deck.slides.items[record.slideIndex];
 const prefix=path.join(dir,`slide-${record.slideIndex+1}`);
 await fs.writeFile(prefix+'-before.png',new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
 deck.resolve(record.id).text.replace(before,after);
 await fs.writeFile(prefix+'-after.png',new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
}
await (await PresentationFile.exportPptx(deck)).save(path.join(dir,'candidate.pptx'));
for(const [index,slide] of deck.slides.items.entries()){
 await fs.writeFile(path.join(dir,`slide-${index+1}.png`),new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
}
console.log('Edited and rendered 21 slides');
