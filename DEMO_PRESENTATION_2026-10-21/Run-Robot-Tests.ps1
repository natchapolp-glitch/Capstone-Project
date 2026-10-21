$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$robotPython = Join-Path $env:USERPROFILE 'SeminarLab\.venv-robot\Scripts\python.exe'
if (!(Test-Path -LiteralPath $robotPython)) { throw 'Robot test environment is missing. See ROBOT_TEST_README.md.' }
& (Join-Path $PSScriptRoot 'Start-Demo.ps1') -NoBrowser
$resultPath = Join-Path $PSScriptRoot ('robot_results\run-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
Write-Host 'Running real Chrome UI tests. A clearly labelled automated test purchase will become the latest HA state.'
& $robotPython -m robot --outputdir $resultPath (Join-Path $repoPath 'tests\robot\demo_presentation.robot')
if ($LASTEXITCODE -ne 0) { throw "Robot tests failed. Open $resultPath\report.html" }
Write-Host "PASS. Report: $resultPath\report.html" -ForegroundColor Green
