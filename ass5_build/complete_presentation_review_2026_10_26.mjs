import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/NATCHAPOL/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=process.cwd(), output=path.join(root,'PRESENTATION_READY_2026-10-26');
const build=path.join(root,'.codex-finalizer/review-complete-2026-10-26');
await fs.mkdir(build,{recursive:true});
let script=await fs.readFile(path.join(output,'SCRIPT_10_MIN_2_SPEAKERS.md'),'utf8');
script=script.replace('ใช้กับ Ass5_REVIEWED_2026-10-26.pptx','ใช้กับ Ass5_10MIN_REVIEWED_v2_2026-10-26.pptx');
script=script.replace('ตารางนี้เป็นค่าดิบที่ใช้ทดสอบการส่ง ไม่ใช่ยอดซื้อที่รับรองว่าถูกครับ ต่อไปเป็นคลิปรันบน PC แสดงการอ่านภาพ ตรวจแก้โดยผู้ใช้ และส่งถึง Home Assistant ครับ',
 'ตารางนี้เป็นค่าดิบจากการทดสอบการส่ง ส่วนเดโมต่อไปจะแสดงภาพ ข้อความที่อ่านได้ การตรวจแก้ และการเชื่อมถึง Home Assistant บน PC ครับ');
script=script.replace('**เปิดคลิปที่บันทึกเสร็จและตรวจแล้ว ไม่พูดทับบทพากย์ เมื่อจบกลับสไลด์ 19**',
 '**เลือกคำเปิดให้ตรงสิ่งที่แสดง:** ถ้ามีคลิปที่ตรวจแล้ว พูดว่า “ขอเปิดคลิปที่บันทึกไว้ครับ” ถ้าใช้ผลบันทึกในเบราว์เซอร์ พูดว่า “ขอเปิดผลย้อนหลังจากรอบที่ระบบบันทึกไว้ครับ” และหากเป็นผล Robot ต้องบอกว่าเป็นข้อมูลสังเคราะห์สำหรับทดสอบการส่ง\n\n**ใช้คู่มือ DEMO_2_MIN_RUNBOOK.md จำกัดช่วงสาธิต 2 นาที เมื่อจบกลับสไลด์ 19 คลิปยังต้องอัด/ตรวจจริงก่อนเลือกวิธีคลิป**');
script=script.replace('ส่วนผลจากภาพจริงจะอยู่ในคลิปเดโมครับ','ส่วนผลจากภาพจริงจะอยู่ในช่วงเดโมครับ');
script=script.replace('ผลเวลานี้เป็นคนละรอบกับคลิป','ผลเวลานี้เป็นรอบทดลองเดิม แยกจากการสาธิตวันนี้');
script += '\n\n## จุดตรวจเวลาซ้อม\n\n- ถึงหน้า 8 ที่ 2:10, ส่งต่อหลังหน้า 13 ที่ 3:50\n- เข้าหน้า 18 ที่ 5:20 และออกจากเดโมไม่เกิน 7:35\n- จบหน้า 19 ที่ 8:15 และจบทั้งชุดที่ 9:00\n- หากช้าเกิน 30 วินาที ให้พูดแต่ใจความของหน้าถัดไปและคงข้อจำกัดสำคัญ ไม่ตัดช่วงสรุปทิ้ง\n- จับเวลารวมการคลิกและสลับหน้าต่างจริงสองรอบ ต้องจบไม่เกิน 9:30 ก่อนใช้แผนนี้เป็นเวลานัดหมาย\n- เวลาที่ให้เป็นแผนซ้อม ยังไม่ใช่ผลจับเวลามนุษย์ ไม่อ่านตารางทั้งหน้า 17–19 และไม่อธิบายศัพท์ทุกตัวระหว่างพรี ใช้ QA_ALL_21_SLIDES.md เตรียมตอบเพิ่มเติม\n';
await fs.writeFile(path.join(output,'SCRIPT_10_MIN_REVIEWED_v2.md'),script);
const sections=[...script.matchAll(/^### (\d+) — ([^\n]+)\n([\s\S]*?)(?=^### |^## |$(?![\s\S]))/gm)];
if(sections.length!==21)throw Error('Expected 21 speaking sections, got '+sections.length);
const source=path.join(output,'Ass5_REVIEWED_2026-10-26.pptx');
const deck=await PresentationFile.importPptx(await FileBlob.load(source));
const inspection=await deck.inspect({kind:'slide,textbox,table,notes,layout',maxChars:500000});
await fs.writeFile(path.join(build,'import_inspection.json'),JSON.stringify(inspection.records,null,2));
const previous=JSON.parse(await fs.readFile(path.join(build,'source_content.json'),'utf8'));
for(const section of sections){
 const n=Number(section[1]);
 deck.slides.items[n-1].speakerNotes.text=`${n<=13?'ธนบดี':'ณัชพล'} | หน้า ${n} | ${section[2]}\n\nบทพูดหลักในเวลา 10 นาที\n${section[3].trim()}\n\nรายละเอียดสำหรับตอบคำถาม ไม่อ่านทั้งหมดระหว่างพรี\n${previous[n-1].original_notes}`;
}
for(const [before,after] of [
 ['เดโมภาพจริงส่งข้อมูลถึง Home Assistant ได้แล้ว','ผลทดสอบบน PC: ส่งข้อมูลถึง Home Assistant'],
 ['ผลทดสอบการส่งข้อมูลบน PC ก่อนมนุษย์ตรวจแก้; คลิปแสดงขั้นตรวจแก้จริง','ผลทดสอบการส่งค่าดิบบน PC; ขั้นตรวจแก้แสดงแยกในเดโม'],
]){
 const record=inspection.records.find(r=>r.kind==='textbox'&&r.text?.includes(before));
 if(!record)throw Error('Missing exact anchor: '+before);
 deck.resolve(record.id).text.replace(before,after);
}
await (await PresentationFile.exportPptx(deck)).save(path.join(build,'candidate.pptx'));
const slide=deck.slides.items[17];
await fs.writeFile(path.join(build,'slide-18.png'),new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
await fs.writeFile(path.join(build,'speaking_sections.json'),JSON.stringify(sections.map(s=>({slide:Number(s[1]),heading:s[2],text:s[3].trim()})),null,2));
console.log('Updated all 21 speaker notes and slide 18; candidate saved');
