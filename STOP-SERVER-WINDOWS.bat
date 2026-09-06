@echo off
rem ============================================================
rem  TERRA BATTLE SERVER - STOPPER (Windows)
rem  Safely stops only the Terra Battle server processes.
rem  Uses PowerShell CIM (wmic is gone on Windows 11 24H2+).
rem ============================================================
title Terra Battle Server - Stopper

set "KILLED=0"

rem --- kill only python.exe processes whose command line runs bootstrap_server ---
for /f "usebackq tokens=2" %%P in (`powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*bootstrap_server*' } | Select-Object -ExpandProperty ProcessId" 2^>nul`) do (
    if not "%%P"=="" (
        echo Killing server process PID %%P ...
        taskkill /PID %%P /F >nul 2>nul
        set "KILLED=1"
    )
)

if "%KILLED%"=="0" (
    echo No running Terra Battle server found.
) else (
    echo Server stopped.
)

rem --- verify port 18696 is free ---
timeout /t 2 /nobreak >nul
netstat -ano | findstr ":18696" | findstr "LISTENING" >nul 2>nul
if %errorlevel%==0 (
    echo WARNING: port 18696 still in use - close the server window manually.
) else (
    echo Port 18696 is free.
)
pause
