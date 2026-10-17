$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pptx = Join-Path $root 'ass5_output\Residential_Intelligence_Project_Progress_READY_2026-10-18.pptx'
$pptPdf = [System.IO.Path]::ChangeExtension($pptx, '.pdf')
$docx = Join-Path $root 'ass6_output\Residential_Intelligence_Computer_Project_Proposal_READY_2026-10-18.docx'
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
$profile = 'file:///C:/Users/NATCHAPOL/SeminarLab/qa_ass56/lo_restore_base_20261018'
& $lo "-env:UserInstallation=$profile" '--headless' '--convert-to' 'pdf' '--outdir' (Split-Path -Parent $docPdf) $docx
if (-not (Test-Path -LiteralPath $docPdf)) { throw "LibreOffice did not create $docPdf" }
Write-Output $pptPdf
Write-Output $docPdf
