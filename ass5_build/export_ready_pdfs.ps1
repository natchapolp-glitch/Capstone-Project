$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pptx = Join-Path $root 'ass5_output\Residential_Intelligence_Project_Progress_READY_2026-10-17.pptx'
$pptPdf = [System.IO.Path]::ChangeExtension($pptx, '.pdf')
$docx = Join-Path $root 'ass6_output\Residential_Intelligence_Computer_Project_Proposal_READY_2026-10-17.docx'
$docPdf = [System.IO.Path]::ChangeExtension($docx, '.pdf')

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

$lo = 'C:\Program Files\LibreOffice\program\soffice.exe'
$profile = 'file:///C:/Users/NATCHAPOL/SeminarLab/qa_ass56/lo_ready_profile'
if (Test-Path -LiteralPath $docPdf) { Remove-Item -LiteralPath $docPdf -Force }
& $lo "-env:UserInstallation=$profile" '--headless' '--convert-to' 'pdf' '--outdir' (Split-Path -Parent $docPdf) $docx
for ($attempt = 0; $attempt -lt 60 -and -not (Test-Path -LiteralPath $docPdf); $attempt++) {
    Start-Sleep -Milliseconds 500
}
if (-not (Test-Path -LiteralPath $docPdf)) { throw "LibreOffice did not create $docPdf" }

Write-Output $pptPdf
Write-Output $docPdf
