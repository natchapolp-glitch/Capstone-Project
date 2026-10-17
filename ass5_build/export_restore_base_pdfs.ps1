$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pptx = Join-Path $root 'ass5_output\Residential_Intelligence_Project_Progress_READY_2026-10-18.pptx'
$pptPdf = [System.IO.Path]::ChangeExtension($pptx, '.pdf')
$docx = Join-Path $root 'ass6_output\Residential_Intelligence_Computer_Project_Proposal_READY_2026-10-18.docx'
$docPdf = [System.IO.Path]::ChangeExtension($docx, '.pdf')

# Make per-user fonts visible to Office in this Windows session.
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class SeminarFontLoader {
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode)]
    public static extern int AddFontResource(string path);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern IntPtr SendMessageTimeout(IntPtr hwnd, uint msg, IntPtr w, IntPtr l, uint flags, uint timeout, out IntPtr result);
}
'@
$fontDir = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
Get-ChildItem -LiteralPath $fontDir -Filter 'THSarabunNew*.ttf' | ForEach-Object {
    [void][SeminarFontLoader]::AddFontResource($_.FullName)
}
$fontResult = [IntPtr]::Zero
[void][SeminarFontLoader]::SendMessageTimeout([IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 2, 1000, [ref]$fontResult)

$powerpoint = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $deck = $powerpoint.Presentations.Open($pptx, $true, $false, $false)
    $deck.SaveAs($pptPdf, 32)
}
finally {
    if ($deck -ne $null) { $deck.Close() }
    $powerpoint.Quit()
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$document = $null
try {
    if (-not (@($word.FontNames) -contains 'TH Sarabun New')) { throw 'Word cannot see TH Sarabun New; refusing font-substituted export.' }
    $document = $word.Documents.Open($docx, $false, $true)
    $document.Repaginate()
    $document.ExportAsFixedFormat($docPdf, 17)
}
finally {
    if ($document -ne $null) { $document.Close(0) }
    $word.Quit()
}
if (-not (Test-Path -LiteralPath $docPdf)) { throw "Word did not create $docPdf" }
Write-Output $pptPdf
Write-Output $docPdf
