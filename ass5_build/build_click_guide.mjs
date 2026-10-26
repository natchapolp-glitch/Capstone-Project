import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(path.join(process.execPath, '..', 'package.json'));
const {marked} = require('marked');
const folder = path.resolve('PRESENTATION_READY_2026-10-26');
const md = fs.readFileSync(path.join(folder, 'CLICK_BY_CLICK_GUIDE.md'), 'utf8');
let body = marked.parse(md);
const sections = [];
body = body.replace(/<h2>(.*?)<\/h2>/g, (_, title) => {
  const id = `step-${sections.length + 1}`;
  sections.push({id, title});
  return `<h2 id="${id}">${title}</h2>`;
});
const html = `<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>คู่มือกดตามทีละขั้น — เดโมและพรี 10 นาที</title>
<style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eef3f6;color:#203547;font:18px/1.8 Tahoma,"Leelawadee UI",sans-serif}
header{background:#193149;color:#fff;padding:22px 5vw}header strong{font-size:24px}header p{margin:5px 0}button{font:inherit;cursor:pointer;padding:6px 16px;border-radius:6px;border:1px solid #91b1c4;background:#fff;color:#193149}
.layout{display:grid;grid-template-columns:280px minmax(0,1fr);max-width:1550px;margin:auto;gap:24px;padding:24px}nav{align-self:start;position:sticky;top:12px;background:#fff;border-radius:12px;padding:18px;max-height:94vh;overflow:auto;font-size:15px}nav a{display:block;padding:8px 0;border-bottom:1px solid #e4eaee}main{background:#fff;border-radius:12px;padding:28px 36px;min-width:0}h1{font-size:30px;line-height:1.5;margin-top:0}h2{font-size:25px;color:#075e79;border-top:3px solid #dce8ee;padding-top:24px;margin-top:42px;scroll-margin-top:18px}h3{font-size:21px}a{color:#006687;overflow-wrap:anywhere}p,li{overflow-wrap:anywhere}li{margin:9px 0}li p{margin:8px 0}table{width:100%;border-collapse:collapse;margin:22px 0;font-size:16px}th,td{border:1px solid #cad8e0;padding:12px;text-align:left;vertical-align:top}th{background:#e8f1f5}img{display:block;max-width:100%;height:auto;border:1px solid #b8cbd7;border-radius:8px;margin:22px auto}code{font-size:.88em;background:#edf3f6;padding:2px 5px;overflow-wrap:anywhere}pre{background:#edf3f6;padding:16px;white-space:pre-wrap}blockquote{margin:18px 0;padding:10px 20px;border-left:5px solid #1684a0;background:#eff8fa}input[type=checkbox]{width:18px;height:18px}
@media(max-width:1000px){.layout{grid-template-columns:1fr;padding:12px}nav{position:static;max-height:none}main{padding:20px}table{font-size:14px}td,th{padding:7px}}
@media print{header,nav{display:none}.layout{display:block;padding:0}body{background:white;font-size:11pt}main{padding:0}h2{break-after:avoid}img,tr{break-inside:avoid}a{color:inherit}table{font-size:9pt}}
</style>
<header><strong>คู่มือใช้งานและซ้อมพรี • 10 นาที</strong><p>ทำครั้งแรก: หัวข้อ 2–6 · วันพรี: หัวข้อ 7–8 · มีปัญหา: หัวข้อ 10</p><button onclick="window.print()">พิมพ์คู่มือ</button></header>
<div class="layout"><nav aria-label="สารบัญ"><strong>กดข้ามไปหัวข้อ</strong>${sections.map(s=>`<a href="#${s.id}">${s.title}</a>`).join('')}<a href="START_HERE.md">ไฟล์ทั้งหมดในชุดพรี</a></nav><main>${body}</main></div></html>`;
fs.writeFileSync(path.join(folder, 'CLICK_BY_CLICK_GUIDE.html'), html, 'utf8');
console.log(`Built guide: ${sections.length} sections`);
