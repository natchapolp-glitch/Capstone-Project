$ErrorActionPreference = 'Stop'

$workspace = Split-Path -Parent $PSScriptRoot
$privateBuild = 'C:\Users\NATCHAPOL\SeminarLab\build_ass5'
$outDir = Join-Path $workspace 'ass5_output'
$outFile = Join-Path $outDir 'eEye_Project_Progress_Presentation_2026-10-17.pptx'
$pdfFile = Join-Path $outDir 'eEye_Project_Progress_Presentation_2026-10-17.pdf'
$previewDir = Join-Path $privateBuild 'preview'
New-Item -ItemType Directory -Path $privateBuild, $outDir, $previewDir -Force | Out-Null
$chartSource = Join-Path $workspace 'ass5_assets\eda_itemized_59.png'
$chart = Join-Path $privateBuild 'eda_itemized_59.png'
Copy-Item -LiteralPath $chartSource -Destination $chart -Force

function RGB([int]$r,[int]$g,[int]$b) { return ($r + 256*$g + 65536*$b) }
$navy = RGB 17 50 77
$teal = RGB 14 129 134
$ink = RGB 32 47 58
$muted = RGB 88 105 116
$orange = RGB 205 104 42
$green = RGB 50 134 97
$paper = RGB 249 251 252
$rule = RGB 212 224 229

function Add-Text($slide,[string]$value,[double]$x,[double]$y,[double]$w,[double]$h,[int]$size,[int]$color,[bool]$bold=$false,[int]$align=1) {
    $shape = $slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.TextRange.Text = $value
    $shape.TextFrame.TextRange.Font.Name = 'Tahoma'
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Bold = $(if($bold){-1}else{0})
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $align
    return $shape
}
function Add-Rect($slide,[double]$x,[double]$y,[double]$w,[double]$h,[int]$fill,[int]$lineColor=-1,[double]$lineWidth=0) {
    $shape = $slide.Shapes.AddShape(1,$x,$y,$w,$h)
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $fill
    if ($lineColor -ge 0) { $shape.Line.Visible = -1; $shape.Line.ForeColor.RGB=$lineColor; $shape.Line.Weight=$lineWidth }
    else { $shape.Line.Visible = 0 }
    return $shape
}
function Add-Line($slide,[double]$x1,[double]$y1,[double]$x2,[double]$y2,[int]$color,[double]$width=2) {
    $shape = $slide.Shapes.AddLine($x1,$y1,$x2,$y2)
    $shape.Line.ForeColor.RGB=$color
    $shape.Line.Weight=$width
    return $shape
}
function Add-Base($deck,[string]$title,[int]$number,[string]$subtitle='') {
    $slide=$deck.Slides.Add($deck.Slides.Count+1,12)
    $slide.Background.Fill.Solid()
    $slide.Background.Fill.ForeColor.RGB=$paper
    Add-Rect $slide 0 0 12 540 $teal | Out-Null
    Add-Text $slide $title 48 35 855 47 28 $navy $true | Out-Null
    if ($subtitle) { Add-Text $slide $subtitle 50 88 830 32 15 $muted | Out-Null }
    Add-Line $slide 49 484 906 484 $rule 1 | Out-Null
    Add-Text $slide 'โครงงาน e-Eye  |  ผลทดลองเบื้องต้นบน PC  |  17 ต.ค. 2569' 50 493 750 19 10 $muted | Out-Null
    Add-Text $slide ([string]$number) 876 493 28 19 10 $muted $false 3 | Out-Null
    return $slide
}

$app=$null; $deck=$null
try {
    $app=New-Object -ComObject PowerPoint.Application
    $deck=$app.Presentations.Add()
    $deck.PageSetup.SlideWidth=960
    $deck.PageSetup.SlideHeight=540

    # 1. Title
    $s=Add-Base $deck 'การนำเสนอความก้าวหน้าโครงงาน' 1 'โครงงานคอมพิวเตอร์  สาขาวิชาวิทยาการคอมพิวเตอร์'
    Add-Text $s "การพัฒนาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัย`nเพื่อสกัดและวิเคราะห์ข้อมูลห่วงโซ่อุปทานในครัวเรือน`nด้วยปัญญาประดิษฐ์ประมวลผลเฉพาะถิ่น" 51 140 848 143 24 $ink $true | Out-Null
    Add-Rect $s 52 286 123 5 $teal | Out-Null
    Add-Text $s 'ณัชพล เพ็งพล  |  ธนบดี เริ่มรักสกุล' 53 321 770 30 19 $ink | Out-Null
    Add-Text $s 'อาจารย์ที่ปรึกษา ผศ.บุญทรัพย์ ไวคำ' 53 361 770 27 17 $muted | Out-Null
    Add-Text $s 'สาขาวิชาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยขอนแก่น' 53 402 800 24 15 $muted | Out-Null

    # 2. Architecture
    $s=Add-Base $deck 'ภาพรวม e-Senses ของบ้าน' 2 'ระยะทดลองปัจจุบันศึกษา e-Eye'
    Add-Text $s 'Home Digital Nervous System' 326 138 335 37 22 $navy $true 2 | Out-Null
    Add-Line $s 481 179 481 221 $rule 2 | Out-Null
    Add-Line $s 185 221 775 221 $rule 2 | Out-Null
    foreach($x in @(185,481,775)){ Add-Line $s $x 221 $x 245 $rule 2 | Out-Null }
    Add-Rect $s 58 245 255 113 $teal | Out-Null
    Add-Text $s 'e-Eye' 78 263 212 35 25 (RGB 255 255 255) $true 2 | Out-Null
    Add-Text $s 'ภาพใบซื้อสินค้า / เอกสาร' 76 308 216 28 17 (RGB 255 255 255) $false 2 | Out-Null
    Add-Rect $s 355 245 255 113 (RGB 231 238 241) | Out-Null
    Add-Text $s 'e-Nose' 377 263 208 35 25 $ink $true 2 | Out-Null
    Add-Text $s 'ก๊าซ / VOC: แผนต่อยอด' 369 308 225 28 16 $muted $false 2 | Out-Null
    Add-Rect $s 650 245 255 113 (RGB 231 238 241) | Out-Null
    Add-Text $s 'e-Skin' 670 263 214 35 25 $ink $true 2 | Out-Null
    Add-Text $s 'น้ำหนัก / สัมผัส: แผนต่อยอด' 661 308 234 28 16 $muted $false 2 | Out-Null
    Add-Text $s 'ขอบเขต: ภาพ → ตรวจบริเวณเอกสาร → OCR นำร่อง → JSON (แผนถัดไป)' 62 398 850 37 19 $ink | Out-Null

    # 3. Research question & scope
    $s=Add-Base $deck 'คำถามวิจัยและขอบเขตระยะนี้' 3 'ประเมินความแม่นยำควบคู่กับทรัพยากรที่ใช้'
    Add-Text $s 'ระบบเฉพาะถิ่นจะอ่านใบซื้อสินค้าจริงได้แม่นยำเพียงใด เมื่อภาพและทรัพยากรเปลี่ยน?' 53 147 835 88 26 $navy $true | Out-Null
    Add-Line $s 53 258 904 258 $rule 2 | Out-Null
    Add-Text $s 'ทดลองแล้ว' 55 285 170 32 20 $teal $true | Out-Null
    Add-Text $s 'คัดภาพจริง  •  EDA  •  YOLOv8n บน CPU  •  OCR นำร่อง  •  RKNN SDK บน PC' 55 324 805 67 19 $ink | Out-Null
    Add-Text $s 'ยังไม่ทดสอบ' 55 410 170 28 18 $orange $true | Out-Null
    Add-Text $s 'LLM/JSON ที่มีเฉลยตรวจซ้ำ และความเร็ว/พลังงานของ RK3588 NPU จริง' 230 410 655 45 17 $muted | Out-Null

    # 4. Intake
    $s=Add-Base $deck 'ภาพจริงที่ใช้: คัดครบก่อนทดลอง' 4 'จำนวนภาพไม่เท่ากับจำนวนธุรกรรมอิสระ'
    Add-Text $s '124' 56 136 198 78 52 $navy $true | Out-Null
    Add-Text $s 'ไฟล์ที่รับ' 58 209 175 30 18 $muted | Out-Null
    Add-Text $s '113' 337 136 197 78 52 $navy $true | Out-Null
    Add-Text $s 'ภาพ SHA-256 ไม่ซ้ำ' 339 209 220 30 18 $muted | Out-Null
    Add-Text $s '59' 675 136 190 78 52 $teal $true | Out-Null
    Add-Text $s 'ภาพผู้สมัครใบซื้อสินค้า' 677 209 228 30 18 $muted | Out-Null
    Add-Line $s 55 270 900 270 $rule 2 | Out-Null
    Add-Text $s 'ชุดหลัก 59 ภาพ: พิมพ์ 41 / เขียนมือ 18' 57 300 805 31 21 $ink $true | Out-Null
    Add-Text $s 'ชุดเสริม: ใบรับเงิน 28, ใบแจ้งหนี้ค่าหอ 14, เอกสารอื่นและกรณีพิเศษ 12' 57 350 817 65 18 $ink | Out-Null
    Add-Text $s 'คัดชนิดจากภาพโดยผู้ช่วย; ยังมี 1 ภาพรอตรวจละเอียด และผู้วิจัยต้องตรวจซ้ำ' 57 431 832 31 15 $muted | Out-Null

    # 5. EDA safe figure
    $s=Add-Base $deck 'EDA: ชุดใบซื้อสินค้ามี 59 ภาพ' 5 'สถิติแสงวัดทั้งภาพ รวมฉากหลัง'
    $null=$s.Shapes.AddPicture($chart,0,-1,50,133,860,250)
    Add-Text $s 'ภาพแนวตั้ง 38 / แนวนอน 21   •   ความสว่างมัธยฐาน 173.9/255' 57 411 845 30 18 $ink $true | Out-Null
    Add-Text $s 'ยังไม่ได้วัดมุมเอียงและความหนาแน่นอักษรไทย/อังกฤษ' 57 445 840 25 15 $muted | Out-Null

    # 6. Detector method
    $s=Add-Base $deck 'วิธีทดลอง YOLOv8n บน PC' 6 'เป้าหมายเป็นกรอบ receipt_region หนึ่งบริเวณต่อภาพ'
    Add-Text $s '48 ภาพฉากเดิม' 58 142 299 42 25 $navy $true | Out-Null
    Add-Text $s '38 ฝึก   /   10 ตรวจ' 58 202 345 48 24 $teal $true | Out-Null
    Add-Text $s 'ภาพใหม่ต่างฉาก' 526 142 327 42 25 $navy $true | Out-Null
    Add-Text $s '6 กันไว้ทดสอบ' 526 202 339 48 24 $orange $true | Out-Null
    Add-Line $s 56 280 901 280 $rule 2 | Out-Null
    Add-Text $s 'YOLOv8n pretrained → fine-tune บน CPU → ตรวจทั้งชุดเดิมและชุดใหม่โดยไม่ฝึกเพิ่ม' 58 311 820 76 22 $ink | Out-Null
    Add-Text $s 'ภาพ 5 ใบจากผู้สมัครเดิมกันออกเพราะหลายเอกสารในภาพหรือสงสัยธุรกรรมใกล้ซ้ำ' 58 408 829 46 16 $muted | Out-Null

    # 7. Primary empirical result
    $s=Add-Base $deck 'ผลตรวจจับ: เมื่อเปลี่ยนฉาก คะแนนลดลง' 7 'mAP@0.5 ของโมเดลเดิมที่ไม่ได้ฝึกด้วยภาพใหม่'
    Add-Text $s '0.928' 62 145 333 95 55 $teal $true | Out-Null
    Add-Text $s 'ฉากเดิม 10 ภาพ' 64 240 340 35 21 $ink | Out-Null
    Add-Text $s '0.237' 567 145 331 95 55 $orange $true | Out-Null
    Add-Text $s 'ต่างฉาก 6 ภาพ' 569 240 333 35 21 $ink | Out-Null
    Add-Rect $s 66 306 770 20 (RGB 229 235 238) | Out-Null
    Add-Rect $s 66 306 (770*0.928) 20 $teal | Out-Null
    Add-Rect $s 66 353 770 20 (RGB 229 235 238) | Out-Null
    Add-Rect $s 66 353 (770*0.237) 20 $orange | Out-Null
    Add-Text $s 'ผลเบื้องต้น: n เล็ก, label ตรวจจากภาพโดยผู้ช่วย, ภาพฉากเดิมคล้ายกัน' 66 410 800 43 16 $muted | Out-Null

    # 8. Failure mode
    $s=Add-Base $deck 'กรณีพลาด: กรอบคะแนนสูงสุดจับพื้นหลัง' 8 'ชุดต่างฉากแสดงปัญหา generalization ของตัวตรวจจับ'
    Add-Rect $s 69 151 365 249 (RGB 224 228 230) $rule 1 | Out-Null
    Add-Rect $s 167 207 169 139 (RGB 255 255 255) $teal 2 | Out-Null
    Add-Text $s 'ใบซื้อสินค้า' 190 261 125 30 18 $ink $true 2 | Out-Null
    $frame=Add-Rect $s 80 161 344 229 (RGB 224 228 230) $orange 3
    $frame.Fill.Transparency=1
    Add-Text $s 'กรอบที่ต้องการ' 464 169 401 32 22 $teal $true | Out-Null
    Add-Text $s 'เฉพาะบริเวณกระดาษ' 464 208 397 35 18 $ink | Out-Null
    Add-Text $s 'กรอบที่โมเดลเลือกผิด' 464 276 401 32 22 $orange $true | Out-Null
    Add-Text $s 'ครอบทั้งภาพหรือเพียงบางส่วน' 464 315 410 35 18 $ink | Out-Null
    Add-Text $s 'ภาพต่างฉาก 6 ภาพ: กรอบ confidence สูงสุด IoU≥0.5 เพียง 1 ภาพ' 71 425 829 37 17 $ink $true | Out-Null

    # 9. OCR / virtualization
    $s=Add-Base $deck 'OCR และ RKNN: สถานะจริงของ pipeline' 9 'แยก PC baseline ออกจาก PC-side SDK และบอร์ดจริง'
    Add-Text $s 'EasyOCR ไทย/อังกฤษ' 57 145 401 38 23 $navy $true | Out-Null
    Add-Text $s '3 ภาพพิมพ์' 57 197 395 32 20 $teal $true | Out-Null
    Add-Text $s 'spot-check วันที่/ยอดตรง 4 จาก 6 ช่อง' 57 239 395 70 18 $ink | Out-Null
    Add-Text $s 'ยังไม่ใช่ CER หรือการสกัด field อัตโนมัติ' 57 325 394 56 15 $muted | Out-Null
    Add-Line $s 483 139 483 404 $rule 2 | Out-Null
    Add-Text $s 'RKNN Toolkit2 บน PC' 526 145 381 38 23 $navy $true | Out-Null
    Add-Text $s 'ONNX → RKNN → PC inference: สำเร็จ' 526 197 381 72 19 $green $true | Out-Null
    Add-Text $s 'เป้าหมาย RK3588, float build, output (1,5,2100)' 526 288 380 67 16 $ink | Out-Null
    Add-Text $s 'ยังไม่มี latency / พลังงานจาก NPU จริง' 526 368 376 47 15 $orange | Out-Null

    # 10. Next
    $s=Add-Base $deck 'แผนดำเนินงานต่อ' 10 'ใช้ผลเบื้องต้นกำหนดขั้นพัฒนาและการประเมินระบบ'
    Add-Text $s '1' 58 146 52 48 28 $teal $true | Out-Null
    Add-Text $s 'ตรวจ label และทำเฉลย OCR/JSON โดยคนสองรอบ' 112 148 753 52 21 $ink | Out-Null
    Add-Text $s '2' 58 228 52 48 28 $teal $true | Out-Null
    Add-Text $s 'เพิ่มภาพหลายพื้น แสง และมุม แล้วกันชุดทดสอบใหม่ไว้' 112 230 753 70 21 $ink | Out-Null
    Add-Text $s '3' 58 331 52 48 28 $teal $true | Out-Null
    Add-Text $s 'ทดสอบ JSON/LLM และวัด NPU จริงเมื่อบอร์ดพร้อม' 112 333 753 66 21 $ink | Out-Null
    Add-Text $s 'เค้าโครงโครงงานกำหนดวิธีทดลองและข้อจำกัดจากผล PC ระยะนำร่องนี้' 58 428 814 41 16 $muted | Out-Null

    $deck.SaveAs($outFile)
    for($i=1;$i -le $deck.Slides.Count;$i++) {
        $deck.Slides.Item($i).Export((Join-Path $previewDir ("slide-{0:D2}.png" -f $i)),'PNG',1280,720)
    }
    $deck.SaveAs($pdfFile,32)
    Write-Output "Saved $outFile and $pdfFile, slides=$($deck.Slides.Count)"
}
finally {
    if($deck){$deck.Close()}
    if($app){$app.Quit()}
}
