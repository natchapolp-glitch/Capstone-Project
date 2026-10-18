param([Parameter(Mandatory=$true)][string]$InputPptx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference='Stop'
$InputPptx=[System.IO.Path]::GetFullPath($InputPptx)
$OutputPdf=[System.IO.Path]::GetFullPath($OutputPdf)
$taskPowerPoint=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
    $taskDeck=$taskPowerPoint.Presentations.Open($InputPptx,$true,$false,$false)
    if($taskDeck.Slides.Count -ne 21){throw 'Expected 21 slides'}
    $taskDeck.SaveAs($OutputPdf,32)
    Write-Output "PowerPoint opened $($taskDeck.Slides.Count) slides and exported PDF"
} finally {
    if($null -ne $taskDeck){$taskDeck.Close()}
    $taskPowerPoint.Quit()
}
if(-not (Test-Path -LiteralPath $OutputPdf)){throw 'PDF export missing'}
