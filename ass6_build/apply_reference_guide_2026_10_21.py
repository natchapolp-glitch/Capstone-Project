"""Number-style cited-order option explicitly allowed on pp. 11-12 of user guide."""
from copy import deepcopy
from lxml import etree as E
import re,json
from pathlib import Path
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS={'w':W[1:-1]}
CITE=re.compile(r'\[(\d+(?:\s*[,–-]\s*\d+)*)\]')
def pt(x):return ''.join(x.xpath('.//w:t/text()',namespaces=NS))
def nums(s):
    out=[]
    for part in s.split(','):
        v=re.split('[–-]',part.strip())
        out.extend(range(int(v[0]),int(v[-1])+1))
    return out
def compact(v):
    a=sorted(set(v));groups=[];i=0
    while i<len(a):
        j=i
        while j+1<len(a) and a[j+1]==a[j]+1:j+=1
        groups.append(str(a[i])+'–'+str(a[j]) if j-i>=2 else ', '.join(str(x)for x in a[i:j+1]))
        i=j+1
    return '['+', '.join(groups)+']'
def replace_spans(p,replacements):
    for start,end,value in reversed(replacements):
        nodes=p.xpath('.//w:t',namespaces=NS);pos=0;matches=[]
        for t in nodes:
            n=len(t.text or '')
            if pos<end and pos+n>start:matches.append((t,max(0,start-pos),min(n,end-pos)))
            pos+=n
        for i,(t,a,b)in enumerate(matches):
            t.text=(t.text or '')[:a]+(value if i==0 else '')+(t.text or '')[b:]
            t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')

# Text and bold emphasis segments. The local guide permits bold or italic titles.
# More than six authors: first six followed by et al.; exactly six: list all.
R={
1:('Husom, E. J., Goknil, A., Astekin, M., Shar, L. K., Kåsen, A., Sen, S., et al. (2025).  Sustainable LLM inference for edge AI: Evaluating quantized LLMs for energy efficiency, output accuracy, and inference latency.  ', 'ACM Transactions on Internet of Things', ', 6(4), Article 28.  https://doi.org/10.1145/3767742'),
2:('Giedra, H., Matuzevičius, D., Sledevič, T., Shubitidze, G., & Serackis, A. (2026).  Benchmarking large language model inference on limited-resource edge systems.  ', 'Electronics', ', 15(11), Article 2451.  https://doi.org/10.3390/electronics15112451'),
3:('Zheng, L., Yin, L., Xie, Z., Sun, C., Huang, J., Yu, C. H., et al. (2024).  SGLang: Efficient execution of structured language model programs.  ', 'Advances in Neural Information Processing Systems', ', 37, 62557–62583.  https://doi.org/10.52202/079017-2000'),
4:('ณัชพล เพ็งพล และ ธนบดี เริ่มรักสกุล. (2569).  ', 'ผลนำร่อง e-Eye บน PC ณ 17 ตุลาคม 2569', '.  บันทึกผลภายในโครงงาน.  https://github.com/natchapolp-glitch/Capstone-Project/blob/main/ass5_ready_evidence.md'),
5:('ggml-org. (n.d.).  ', 'GBNF guide, llama.cpp', '.  Retrieved October 21, 2026, from https://github.com/ggml-org/llama.cpp/tree/master/grammars'),
6:('Ultralytics. (n.d.).  ', 'Performance metrics deep dive', '.  Retrieved October 21, 2026, from https://docs.ultralytics.com/guides/yolo-performance-metrics/'),
7:('Tesseract OCR. (n.d.).  ', 'Tessdata', '.  Retrieved October 21, 2026, from https://github.com/tesseract-ocr/tessdata'),
8:('Jaided AI. (n.d.).  ', 'EasyOCR', '.  Retrieved October 21, 2026, from https://github.com/JaidedAI/EasyOCR'),
9:('Rockchip. (n.d.).  ', 'RKNN Toolkit2', '.  Retrieved October 21, 2026, from https://github.com/airockchip/rknn-toolkit2'),
10:('Rockchip. (n.d.).  ', 'RKLLM', '.  Retrieved October 21, 2026, from https://github.com/airockchip/rknn-llm'),
11:('Rockchip. (2022).  ', 'RK3588 brief datasheet', '.  https://www.rock-chips.com/a/en/Products/RK35_Series/2022/0926/1660.html'),
12:('ณัชพล เพ็งพล และ ธนบดี เริ่มรักสกุล. (2569).  ', 'การพัฒนาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัยเพื่อสกัดและวิเคราะห์ข้อมูลห่วงโซ่อุปทานในครัวเรือนด้วยปัญญาประดิษฐ์ประมวลผลเฉพาะถิ่น', '.  รายงานทบทวนวรรณกรรม 32 หน้า, เอกสารภายในโครงงาน.'),
13:('Radxa. (n.d.).  ', 'ROCK 5B product introduction', '.  Retrieved October 21, 2026, from https://docs.radxa.com/en/rock5/rock5b/getting-started/introduction'),
14:('Rivkin, D., Hogan, F., Feriani, A., Konar, A., Sigal, A., Liu, X., et al. (2025).  AIoT smart home via autonomous LLM agents.  ', 'IEEE Internet of Things Journal', ', 12(3), 2458–2472.  https://doi.org/10.1109/JIOT.2024.3471904'),
15:('Sawalha, S., & Al-Naymat, G. (2025).  An adaptive Holt–Winters model for seasonal forecasting of Internet of Things (IoT) data streams.  ', 'IoT', ', 6(3), Article 39.  https://doi.org/10.3390/iot6030039'),
16:('Serepas, F., Papias, I., Christakis, K., Dimitropoulos, N., & Marinakis, V. (2025).  Lightweight embedded IoT gateway for smart homes based on an ESP32 microcontroller.  ', 'Computers', ', 14(9), Article 391.  https://doi.org/10.3390/computers14090391'),
17:('Yin, W., Xu, D., Xu, M., Huang, G., & Liu, X. (2026).  ShadowNPU: System and algorithm co-design for NPU-centric on-device LLM inference.  In ', 'Proceedings of the 24th Annual International Conference on Mobile Systems, Applications and Services', ' (pp. 294–308).  Association for Computing Machinery.  https://doi.org/10.1145/3745756.3809205'),
18:('Cai, F., Yuan, D., Yang, Z., & Cui, L. (2024).  Edge-LLM: A collaborative framework for large language model serving in edge computing.  In ', '2024 IEEE International Conference on Web Services (ICWS)', ' (pp. 799–809).  IEEE.  https://doi.org/10.1109/ICWS62655.2024.00099'),
19:('Moon, S., Cha, J., Park, H., & Kim, J.-Y. (2025).  Hybe: GPU-NPU hybrid system for efficient LLM inference with million-token context window.  In ', 'Proceedings of the 52nd Annual International Symposium on Computer Architecture', ' (pp. 808–820).  Association for Computing Machinery.  https://doi.org/10.1145/3695053.3731051'),
20:('Oloko-Oba, M., Esenogho, E., & Aruleba, K. (2026).  From biosignals to bedside: A review of real-time edge machine learning for wearable health monitoring.  ', 'Bioengineering', ', 13(5), Article 559.  https://doi.org/10.3390/bioengineering13050559'),
21:('Zheng, Y., Chen, Y., Qian, B., Shi, X., Shu, Y., & Chen, J. (2025).  A review on edge large language models: Design, execution, and applications.  ', 'ACM Computing Surveys', ', 57(8), Article 209.  https://doi.org/10.1145/3719664'),
22:('Hu, A., Xu, H., Zhang, L., Ye, J., Yan, M., Zhang, J., et al. (2025).  mPLUG-DocOwl2: High-resolution compressing for OCR-free multi-page document understanding.  In ', 'Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)', ' (pp. 5817–5834).  Association for Computational Linguistics.  https://doi.org/10.18653/v1/2025.acl-long.291'),
23:('ณัชพล เพ็งพล และ ธนบดี เริ่มรักสกุล. (2569).  ', 'ผลทดลองก่อนมีบอร์ด: ข้อความอ้างอิงหนึ่งรอบ OCR Local LLM และการเชื่อม MQTT/Home Assistant', '.  ชุดหลักฐานพร้อมค่าแฮชและข้อจำกัด.  https://github.com/natchapolp-glitch/Capstone-Project/tree/pc-preboard-implementation/reports/preboard')}

def apply(body,qa):
    refs={int(re.match(r'^\[(\d+)\]',pt(x))[1]):x for x in body.findall(W+'p') if re.match(r'^\[\d+\]',pt(x))}
    assert len(refs)==23
    ps=[x for x in body.iter(W+'p') if x not in refs.values()]
    order=[];occurrences=[]
    for x in ps:
        for m in CITE.finditer(pt(x)):
            old=nums(m[1]);occurrences.append(old)
            for n in old:
                assert n in refs,n
                if n not in order:order.append(n)
    assert set(order)==set(refs)
    mapping={n:i+1 for i,n in enumerate(order)}
    for x in ps:
        changes=[(m.start(),m.end(),compact([mapping[n]for n in nums(m[1])]))for m in CITE.finditer(pt(x))]
        replace_spans(x,changes)
    for n,x in refs.items():
        pr=x.find(W+'pPr')
        # Retain source paragraph role, rebuild this reference's content only.
        for ch in list(x):
            if ch.tag!=W+'pPr':x.remove(ch)
        if pr is None:pr=E.Element(W+'pPr');x.insert(0,pr)
        for ch in list(pr):
            if ch.tag in [W+'ind',W+'spacing',W+'jc',W+'keepNext',W+'keepLines']:pr.remove(ch)
        ind=E.SubElement(pr,W+'ind');ind.set(W+'left','360');ind.set(W+'hanging','360')
        sp=E.SubElement(pr,W+'spacing');sp.set(W+'after','100');sp.set(W+'line','240');sp.set(W+'lineRule','auto')
        jc=E.SubElement(pr,W+'jc');jc.set(W+'val','left')
        E.SubElement(pr,W+'keepLines')
        for value,bold in [('['+str(mapping[n])+'] '+R[n][0],False),(R[n][1],True),(R[n][2],False)]:
            r=E.SubElement(x,W+'r');rp=E.SubElement(r,W+'rPr');rf=E.SubElement(rp,W+'rFonts')
            for key in ['ascii','hAnsi','cs','eastAsia']:rf.set(W+key,'TH Sarabun New')
            for tag in ['sz','szCs']:E.SubElement(rp,W+tag).set(W+'val','28')
            if bold:E.SubElement(rp,W+'b');E.SubElement(rp,W+'bCs')
            t=E.SubElement(r,W+'t');t.text=value;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    insertion=min(list(body).index(x)for x in refs.values())
    for x in refs.values():body.remove(x)
    for i,n in enumerate(order):body.insert(insertion+i,refs[n])
    audit={'guide':'คู่มือการเขียนอ้างอิงแบบ APA.pdf','selected_option':'1.2.1 cited-order number, pp. 11-12; reference formatting pp. 13-15, 21, 25-28, 34-40',
           'old_to_new_reference_numbers':mapping,'citation_groups':len(occurrences),'source_count':23,
           'metadata_fixes':['Expanded author lists to guide limit','SGLang Chuyue Sun initial C.','ShadowNPU five actual authors; conference chairs excluded','Undated software documentation uses n.d. with verified access date'],
           'primary_verification_urls':['https://doi.org/10.1145/3745756.3809205','https://proceedings.neurips.cc/paper_files/paper/2024/hash/724be4472168f31ba1c9ac630f15dec8-Abstract-Conference.html','https://ink.library.smu.edu.sg/sis_research/10489/','https://api.crossref.org/works/10.3390/electronics15112451','https://api.crossref.org/works/10.1109/JIOT.2024.3471904','https://doi.org/10.1145/3719664']}
    (qa/'reference_guide_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    return mapping
