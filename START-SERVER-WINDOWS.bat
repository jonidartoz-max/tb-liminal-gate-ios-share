@echo off
rem ============================================================
rem  TERRA BATTLE SERVER - ONE-CLICK STARTER (Windows)
rem  Fully portable: bundled Python runtime. No install, no PATH,
rem  no venv, no pip, no internet needed on the target PC.
rem  Just double-click. The server binds 0.0.0.0 (all interfaces)
rem  on port 18696 - no config file needed.
rem ============================================================
title Terra Battle Server
cd /d "%~dp0"
setlocal enableextensions

rem --- locate a working Python (prefers bundled portable runtime\) ---
call "%~dp0run_common.bat"
if errorlevel 1 (
    echo Python not found. Install from python.org or keep runtime\ folder.
    pause & exit /b 1
)

set "ROOT=%~dp0"
set "SRV=%ROOT%project-liminal-gate"

rem --- extract bundled source if not present ---
if not exist "%SRV%\liminal_gate" (
    echo Extracting server code...
    "%PY%" "%ROOT%extract_code.py"
    if errorlevel 1 ( pause & exit /b 1 )
)

rem --- auto-detect LAN IP so the user knows where to point the IPA ---
rem Use the resolved %PY% path. Write the IP to a temp file via Python to
rem avoid cmd's fragile FOR /F quoting.
set "TB_IP="
"%PY%" -c "import socket,os; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); open(os.path.join(os.environ['TEMP'],'terra_ip.txt'),'w').write(s.getsockname()[0]); s.close()" >nul 2>nul
if exist "%TEMP%\terra_ip.txt" (
    set /p TB_IP=<"%TEMP%\terra_ip.txt"
    del "%TEMP%\terra_ip.txt" >nul 2>nul
)
if "%TB_IP%"=="" set "TB_IP=192.168.1.100"
rem --- detect Tailscale IP if installed (100.x) ---
set "TS_IP="
where tailscale >nul 2>nul && for /f "tokens=1" %%T in ('tailscale ip -4 2^>nul') do set "TS_IP=%%T"

echo.
echo Starting Terra Battle server on port 18696 ...
echo   LAN:       http://%TB_IP%:18696
echo   Tailscale: http://%TS_IP%:18696  ^(if installed; login with your email at https://tailscale.com ^)
echo   On this PC, verify at: http://%TB_IP%:18696/healthz  (should show {"status":"ok"})
echo   Root "/" always shows {"error":"route_not_implemented"} - that is NORMAL
echo   To play from anywhere: install Tailscale on this PC + iPhone, login with
echo   the SAME email, then run PATCH-ME and paste the 100.x IP shown above.
echo.

"%PY%" -m liminal_gate.bootstrap_server ^
  --profile  "%ROOT%profiles\legacy-client-bootstrap.json" ^
  --state-file  "%ROOT%user-data\bootstrap-state.json" ^
  --host 0.0.0.0 --port 18696 ^
  --event-log  "%ROOT%user-data\events.jsonl" ^
  --resource-root  "%ROOT%resources\iOS_2" ^
  --resource-manifest  "%ROOT%user-data\resources.json" ^
  --public-data-root  "%ROOT%user-data\public_data" ^
  --core-story --pacts --hunting --daily-quests --secondary-worlds ^
  --jobs --rebirth --status-items --companion-draw --companion-sale ^
  --companion-strengthen --companion-evolution --trading-post ^
  --drop-eligibility --achievements --summon-skills ^
  --event-catalog "%ROOT%user-data\event-catalog.json" ^
  --character-catalog "%ROOT%user-data\character-catalog.json" ^
  --story-outcome-catalog "%ROOT%user-data\story-outcomes.json" ^
  --companion-equipment-catalog "%ROOT%user-data\companion-equipment.json"

echo.
echo Server stopped.
pause
