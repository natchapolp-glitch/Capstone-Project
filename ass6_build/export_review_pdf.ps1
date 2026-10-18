param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference='Stop'
$InputDocx=[System.IO.Path]::GetFullPath($InputDocx)
$OutputPdf=[System.IO.Path]::GetFullPath($OutputPdf)
$taskWord=New-Object -ComObject Word.Application
$taskWord.Visible=$false
$taskWord.DisplayAlerts=0
try {
    $taskDoc=$taskWord.Documents.Open($InputDocx,$false,$true)
    $taskDoc.Repaginate()
    $taskDoc.ExportAsFixedFormat($OutputPdf,17)
    $taskDoc.Close(0)
} finally {
    $taskWord.Quit()
}
if (-not (Test-Path -LiteralPath $OutputPdf)) {throw 'PDF export did not produce a file'}
Write-Output $OutputPdf
