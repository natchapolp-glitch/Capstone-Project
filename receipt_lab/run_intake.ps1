$python = Join-Path $env:USERPROFILE 'SeminarLab\.venv\Scripts\python.exe'
$script = Join-Path $PSScriptRoot 'intake.py'
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment was not found: $python"
}
& $python $script
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$report = Join-Path $env:USERPROFILE 'SeminarLab\reports'
Write-Host "Reports are in $report"
