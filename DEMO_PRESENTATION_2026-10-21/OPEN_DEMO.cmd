@echo off
setlocal
rem Use Windows' installed PowerShell even when the inherited PATH is incomplete.
set "PATH=%SystemRoot%\System32;%SystemRoot%\System32\WindowsPowerShell\v1.0;%PATH%"
set "DEMO_POWERSHELL=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%DEMO_POWERSHELL%" (
    echo Windows PowerShell was not found at "%DEMO_POWERSHELL%".
    pause
    exit /b 1
)
"%DEMO_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Demo.ps1" %*
set "DEMO_EXIT_CODE=%ERRORLEVEL%"
if not "%DEMO_EXIT_CODE%"=="0" pause
exit /b %DEMO_EXIT_CODE%
