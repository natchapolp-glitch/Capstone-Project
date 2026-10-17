$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'ass5_output\Residential_Intelligence_Project_Progress_REVISED_2026-10-17.pptx'
$target = Join-Path $root 'ass5_output\Residential_Intelligence_Project_Progress_READY_2026-10-17.pptx'
$caption = Join-Path $PSScriptRoot 'slide11_language_caption.txt'
$groupInfo = Join-Path $PSScriptRoot 'slide1_group_info.txt'

$app = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $deck = $app.Presentations.Open($source, $false, $false, $false)
    if ($deck.Slides.Count -ne 17) { throw "Expected 17 slides, found $($deck.Slides.Count)" }
    $groupLines = [System.IO.File]::ReadAllLines($groupInfo, [System.Text.Encoding]::UTF8)
    if ($groupLines.Length -ne 3) { throw 'Expected three lines of project and exam group information' }
    $cover = $deck.Slides.Item(1)
    foreach ($item in @(
        @{ Text = $groupLines[0]; Y = 68; Size = 14; Bold = 0 },
        @{ Text = $groupLines[1]; Y = 96; Size = 29; Bold = -1 },
        @{ Text = $groupLines[2]; Y = 145; Size = 16; Bold = 0 }
    )) {
        $label = $cover.Shapes.AddTextbox(1, 775, $item.Y, 176, 38)
        $label.TextFrame.MarginLeft = 0
        $label.TextFrame.MarginRight = 0
        $label.TextFrame.MarginTop = 0
        $label.TextFrame.MarginBottom = 0
        $label.TextFrame.WordWrap = 0
        $label.TextFrame.TextRange.Text = $item.Text
        $label.TextFrame.TextRange.Font.Name = 'Tahoma'
        $label.TextFrame.TextRange.Font.Size = $item.Size
        $label.TextFrame.TextRange.Font.Bold = $item.Bold
        $label.TextFrame.TextRange.Font.Color.RGB = 16777215
    }
    $slide = $deck.Slides.Item(11)
    $shape = $slide.Shapes.AddTextbox(1, 60, 478, 846, 23)
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = 0
    $shape.TextFrame.TextRange.Text = [System.IO.File]::ReadAllText($caption, [System.Text.Encoding]::UTF8).Trim()
    $shape.TextFrame.TextRange.Font.Name = 'Tahoma'
    $shape.TextFrame.TextRange.Font.Size = 14
    $shape.TextFrame.TextRange.Font.Color.RGB = 7629144
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
    $deck.SaveAs($target, 24)
    Write-Output $target
}
finally {
    if ($deck -ne $null) { $deck.Close() }
    $app.Quit()
}
