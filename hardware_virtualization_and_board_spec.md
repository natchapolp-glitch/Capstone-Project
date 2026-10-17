# แผน Hardware Virtualization และสเปกบอร์ดสำหรับวิทยานิพนธ์ e-Eye

อัปเดต 17 ตุลาคม 2569 ตามอีเมลอาจารย์: ทำขั้นจำลองบนคอมพิวเตอร์ก่อน แล้วจึงขอยืมฮาร์ดแวร์ที่คณะจัดสรรได้โดยยื่นเรื่องพร้อมสเปก รุ่นที่เสนอด้านล่างเป็น **ร่างเพื่อขอจัดหา/ยืม** ไม่ใช่การยืนยันว่าคณะมีรุ่นนี้หรือว่าผล NPU ได้รับการพิสูจน์แล้ว

## ความหมายของ virtualization สำหรับงานนี้

งานวิทยานิพนธ์เน้น **inference/deployment** ของ e-Eye: ภาพใบเสร็จ → ตรวจจับตำแหน่งเอกสาร → OCR ไทย/อังกฤษ → LLM สกัด JSON ไม่ได้ออกแบบสถาปัตยกรรมชิปหรือฝึกโมเดลบน NPU ดังนั้นลำดับการจำลองที่ตรงโจทย์คือ:

| ระดับ | สิ่งที่ทำ | หลักฐานที่ได้ | ข้อจำกัด |
|---|---|---|---|
| 1. Baseline บนโน้ตบุ๊ก | EDA, train/validate YOLO, OCR, LLM, latency/RAM ของเครื่อง | ความแม่นยำและเวลาอ้างอิงของโน้ตบุ๊ก | ไม่ใช่ผล NPU RK3588 |
| 2. PC-side Rockchip SDK | แปลง YOLO → RKNN; ทดสอบ inference/ผลลัพธ์ใน PC-side RKNN Toolkit2; แปลง LLM ที่รองรับ → RKLLM และทดสอบความถูกต้องผ่าน PC-side simulator ตามความสามารถ SDK | โมเดลแปลงได้หรือไม่, ความคลาดเคลื่อนหลัง quantization, ความถูกต้องของผลลัพธ์ | ไม่ใช่การจำลองความเร็ว/กำลังไฟของบอร์ดที่ใช้แทนการวัดจริงได้ |
| 3. บอร์ดจริง | รันโมเดล RKNN/RKLLM บน RK3588; วัด latency, RAM, NPU utilization, พลังงานและความแม่นยำบนข้อมูลชุดเดิม | ข้อสรุปเรื่อง Edge AI จริง | ต้องได้รับบอร์ดและอุปกรณ์ก่อน |

PyTorchSim เป็นตัวจำลอง **NPU แบบทั่วไปที่ผู้วิจัยกำหนดบน RISC-V** รองรับ training และ inference แต่ไม่ได้จำลอง RK3588 โดยตรง จึงใช้ได้หากอาจารย์ต้องการโจทย์ *architectural simulation* เพิ่มเติม ส่วน NeuSim/npsim ก็เป็นงานสำรวจสถาปัตยกรรม/การจัดตาราง NPU; Aicir เน้นวงจรควอนตัมบน Ascend 910B จึงไม่ใช่เครื่องมือหลักของ pipeline ใบเสร็จนี้ ควรแจ้งอาจารย์ว่าเราเสนอ PC-side Rockchip SDK เป็นความหมายเชิงปฏิบัติของ hardware virtualization และขอให้ยืนยันหากต้องการ PyTorchSim โดยเฉพาะ

## งานที่ทำทันทีระหว่างรอใบเสร็จและบอร์ด

1. รับภาพนำร่อง 10–20 ใบ เก็บต้นฉบับนอก OneDrive และทำ manifest/EDA ตรวจความละเอียด แสง มุม และชนิดใบเสร็จ 20 ใบเพียงพอสำหรับ pilot และสาธิตขั้นจำลอง ยังไม่พอสำหรับอ้างอิงความแม่นยำทั่วไปหรือฝึก YOLO ให้ครอบคลุมทุกสภาพ
2. ทำเฉลยข้อความและ JSON แยกกัน พร้อมกรอบใบเสร็จสำหรับภาพที่ต้องใช้ฝึก detector ป้องกันการรั่วของภาพใบเดียวกันหลายมุมข้าม train/test
3. ทดสอบ OCR ไทย/อังกฤษ และ LLM บนโน้ตบุ๊กด้วยข้อมูลชุดเดียวกัน กำหนดตัววัด CER, field accuracy, JSON validity, latency, RAM; รายงานชนิดเครื่องทุกครั้ง
4. ใช้ YOLO รุ่นเล็กที่ฝึก/ปรับกับคลาสใบเสร็จจริง; weights ที่ฝึกบน COCO ทั่วไปไม่ได้หมายความว่าตรวจจับใบเสร็จได้โดยตรง ส่งออก ONNX แล้วแปลงด้วย RKNN Toolkit2 เลือก calibration set จากภาพงานจริงและเทียบผลก่อน/หลัง quantization
5. สำหรับ LLM เลือกรุ่นเล็กที่ **ทั้งรองรับภาษาไทยและอยู่ในรายการที่ RKLLM รองรับ** ตรวจ conversion/quantization และ PC-side inference ก่อนล็อกสเปกบอร์ด ทดลอง JSON schema/grammar ใน llama.cpp ได้ แต่ยังไม่กล่าวว่าฟังก์ชัน grammar เดียวกันทำงานบน RKLLM NPU จนกว่าจะยืนยัน SDK/API
6. จัดตารางผลเป็น 3 คอลัมน์แยกกัน: laptop baseline, PC-side SDK simulation, board measurement; ช่องที่ยังไม่ทดลองให้ระบุ “รอทดสอบ” ไม่มีการเดาตัวเลข NPU จาก TOPS

เครื่องปัจจุบันมี Windows, Intel Core Ultra 7 155H, RAM ประมาณ 16 GB, Python 3.13 และ WSL Ubuntu 26.04/Python 3.14 ส่วน RKNN Toolkit2 รองรับ Python ถึง 3.12 และ RKLLM Toolkit ระบุ Python 3.10–3.12 จึงต้องสร้าง environment ที่ตรงเวอร์ชันสำหรับขั้น Rockchip ก่อนติดตั้ง SDK ใน WSL ไม่ใช้ Python 3.14 ของ WSL ปัจจุบันโดยตรง ขณะนี้ชุดรับภาพ, EDA, GUI ติดป้าย และ Python baseline พร้อมแล้ว; **ยังไม่ได้ติดตั้ง/รัน Rockchip simulator และยังไม่มีผลจำลอง NPU**

## สเปกที่เสนอขอยืมจากคณะ

**รุ่นอ้างอิง: Radxa ROCK 5B, RK3588, RAM 16 GB** (หรือบอร์ด RK3588 ที่เทียบเท่าซึ่งคณะมี พร้อมยืนยัน image OS, SDK และ runtime ที่ใช้งานได้) เหตุผลที่เลือก 16 GB คือมีพื้นที่ให้ทดสอบ YOLO + OCR/LLM ขนาดเล็กและเก็บ log โดยไม่กดดันหน่วยความจำตั้งแต่ต้น แต่ขนาดโมเดลที่รันจริงยังต้องทดสอบอีกครั้ง

| รายการ | สเปก/เหตุผลที่ใส่ในคำขอ |
|---|---|
| SoC/NPU | Rockchip RK3588; NPU สูงสุด 6 TOPS ตามข้อมูลผู้ผลิต; รองรับ RKNN Toolkit2 และ RKLLM SDK |
| RAM | 16 GB LPDDR4X สำหรับ ROCK 5B (หากมีเฉพาะ 8 GB ให้ทดลองความพอของ RAM ก่อนตกลงขอบเขต LLM) |
| OS/SDK | Linux image สำหรับบอร์ดที่มี NPU driver/runtime เข้ากับ RKNN/RKLLM เวอร์ชันที่ใช้ ขอระบุเวอร์ชันตอนรับมอบ |
| Storage | eMMC หรือ microSD อย่างน้อย 64 GB สำหรับ OS, โมเดล, ชุดข้อมูลทดสอบและ log; ตรวจอุปกรณ์ที่มีจริง |
| Input/connection | USB camera หรือรับภาพจาก IP camera/ไฟล์ผ่าน Ethernet; ROCK 5B มี Ethernet 2.5G และ USB camera ใช้เป็นทางเริ่มต้นได้ |
| อุปกรณ์ร่วม | อะแดปเตอร์ USB-C PD ที่เข้ากับบอร์ด, สื่อบันทึกพร้อม OS, ชุดระบายความร้อน, สาย Ethernet/USB, กล้องหากทดสอบภาพสด; เครื่องวัดกำลังไฟถ้าต้องรายงาน energy per receipt |

**เกณฑ์รับบอร์ด:** บูต OS ได้, ระบุ RK3588/RAM ได้, NPU driver และตัวอย่าง RKNN/RKLLM รันได้, เข้าถึงบอร์ดทางเครือข่ายได้, มีไฟเลี้ยงและระบายความร้อนเหมาะสม หากคณะเสนอรุ่นอื่น ให้ตรวจเกณฑ์เหล่านี้กับ RAM/SDK ก่อนรับแทน ไม่ซื้อบอร์ดเองในตอนนี้

## ข้อความร่างสำหรับส่งอาจารย์/เจ้าหน้าที่ (ยังไม่ได้ส่ง)

> ตามคำแนะนำ ผมจะทำการทดสอบบนคอมพิวเตอร์และ PC-side simulator ของ Rockchip ก่อน โดยตรวจการแปลงโมเดล YOLO เป็น RKNN และ LLM เป็น RKLLM รวมถึงความถูกต้องหลัง quantization จากนั้นจึงวัด latency/RAM/พลังงานบนบอร์ดจริง ผมขอทำเรื่องยืมบอร์ดอ้างอิง Radxa ROCK 5B (RK3588, RAM 16 GB) หรือรุ่น RK3588 เทียบเท่าที่คณะมี พร้อมอะแดปเตอร์ไฟเลี้ยง สื่อบันทึก OS ชุดระบายความร้อน และอุปกรณ์รับภาพ หากอาจารย์หมายถึงการจำลองสถาปัตยกรรม NPU ด้วย PyTorchSim โดยเฉพาะ รบกวนช่วยยืนยันขอบเขตผลทดลองที่ต้องการด้วยครับ

## หลักฐานอ้างอิง

- [Rockchip RKNN Toolkit2 README](https://github.com/airockchip/rknn-toolkit2/blob/master/README.md): รองรับ RK3588, model conversion, inference และ evaluation บน PC/บอร์ด, Python ถึง 3.12
- [Rockchip RKLLM README](https://github.com/airockchip/rknn-llm/blob/main/README.md) และ [changelog](https://github.com/airockchip/rknn-llm/blob/main/CHANGELOG.md): รุ่นโมเดล/แพลตฟอร์มที่รองรับ, Python 3.10–3.12, PC-side simulation accuracy/inference
- [Radxa ROCK 5B specification](https://docs.radxa.com/en/rock5/rock5b/getting-started/introduction): RK3588, RAM, NPU, I/O และ power
- [PyTorchSim project](https://github.com/PSAL-POSTECH/PyTorchSim): ตัวจำลอง RISC-V NPU เพื่อศึกษาสถาปัตยกรรม ไม่ใช่ RK3588 emulator
- [NeuSim project](https://github.com/platformxlab/NeuSim): ตัวจำลองสมรรถนะ/พลังงานสำหรับสำรวจการออกแบบ NPU ทั่วไป
- [npsim paper](https://ieeexplore.ieee.org/document/11630789/): ตัวจำลอง CPU–NPU เพื่อศึกษาการจัดตารางงาน
- [Aicir paper](https://arxiv.org/html/2608.09733v1): ตัวจำลองวงจรควอนตัมบน Ascend NPU
