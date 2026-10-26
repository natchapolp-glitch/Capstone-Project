param([switch]$NoBrowser, [switch]$SavedResultsOnly)
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$demoPython = Join-Path $env:USERPROFILE 'SeminarLab\.venv\Scripts\python.exe'
$logFolder = Join-Path $env:USERPROFILE 'SeminarLab\preboard\services'
if (!(Test-Path -LiteralPath $demoPython)) { throw "Missing demo Python: $demoPython" }
Push-Location -LiteralPath $repoPath
try {
    if (!$SavedResultsOnly) {
        & $demoPython -m receipt_lab.preboard.demo_preflight
        if ($LASTEXITCODE -ne 0) { throw 'Live inference runtime is unavailable. Inspect the error above, or explicitly use -SavedResultsOnly for historical results.' }
    }
    Write-Host 'Starting MQTT and Home Assistant...'
    & $demoPython -m receipt_lab.preboard.services start
    if ($LASTEXITCODE -ne 0) { throw 'Could not start local services' }
    & $demoPython -m receipt_lab.preboard.services configure
    if ($LASTEXITCODE -ne 0) { throw 'Home Assistant is not ready; inspect private service logs' }
    $health = $null
    try { $health = Invoke-RestMethod 'http://127.0.0.1:8090/health' -TimeoutSec 3 } catch {}
    if (!$health) {
        if (Get-NetTCPConnection -LocalPort 8090 -State Listen -ErrorAction SilentlyContinue) {
            throw 'Port 8090 is occupied by another service. No process was stopped.'
        }
        Start-Process -FilePath $demoPython -ArgumentList '-m','receipt_lab.demo_pc.server' -WorkingDirectory $repoPath -WindowStyle Hidden -RedirectStandardOutput "$logFolder\demo-present.stdout.log" -RedirectStandardError "$logFolder\demo-present.stderr.log" | Out-Null
        for ($attempt=0; $attempt -lt 30; $attempt++) {
            try { $health = Invoke-RestMethod 'http://127.0.0.1:8090/health' -TimeoutSec 2; break } catch { Start-Sleep -Seconds 1 }
        }
    }
    if ($health.status -ne 'ok' -or $health.database -ne 'ok') { throw 'Demo health check failed' }
    $ha = Invoke-RestMethod 'http://127.0.0.1:8090/api/ha-status' -TimeoutSec 45
    if (!$ha.reachable -or $ha.entities.Count -ne 2) { throw 'The two Home Assistant demo sensors are not ready' }
    & $demoPython -m receipt_lab.preboard.check_ha_frontend
    if ($LASTEXITCODE -ne 0) { throw 'Home Assistant frontend WebSocket check failed. Inspect the private ha.log before presenting.' }
    if ($SavedResultsOnly) {
        Write-Host 'READY FOR SAVED RESULTS ONLY: http://127.0.0.1:8090/demo' -ForegroundColor Yellow
    } else {
        Write-Host 'SERVICES READY: http://127.0.0.1:8090/demo' -ForegroundColor Green
        Write-Host 'Runtime files exist. Run the Robot live test before claiming inference is ready.'
    }
    Write-Host 'Keep this PC awake and plugged in. CPU inference can take several minutes; use a checked clip within the 10-minute presentation.'
    if (!$NoBrowser) { Start-Process 'http://127.0.0.1:8090/demo' }
} finally { Pop-Location }
