@echo off
rem ============================================================
rem  Terra Battle Liminal Gate - shared launcher logic
rem  Finds a working Python, PREFERRING the bundled portable one.
rem  NEVER uses venv or pip -> nothing gets hardcoded to a PC.
rem  On success sets %PY% and exits /b 0.  On failure exits /b 1.
rem ============================================================
set "PY="
set "PY_OK=0"

rem --- 1) bundled portable python (no install, works on any PC) ---
if exist "%~dp0runtime\python.exe" (
    "%~dp0runtime\python.exe" -c "import sys" >nul 2>nul
    if not errorlevel 1 (
        set "PY=%~dp0runtime\python.exe"
        set "PY_OK=1"
        goto :have_python
    )
)

rem --- 2) try each common command in turn ---
for %%C in (py python python3) do (
    if "%PY_OK%"=="0" (
        where %%C >nul 2>nul
        if not errorlevel 1 (
            %%C -c "import sys" >nul 2>nul
            if not errorlevel 1 (
                set "PY=%%C"
                set "PY_OK=1"
            )
        )
    )
)

rem --- 3) scan common install dirs (in case not on PATH) ---
if "%PY_OK%"=="0" (
    for %%D in ("%LocalAppData%\Programs\Python" "C:\Program Files\Python*" "C:\Program Files (x86)\Python*") do (
        if exist "%%~D" if "%PY_OK%"=="0" (
            for /f "delims=" %%E in ('dir /b "%%~D" 2^>nul') do (
                if exist "%%~D\%%E\python.exe" if "%PY_OK%"=="0" (
                    "%%~D\%%E\python.exe" -c "import sys" >nul 2>nul
                    if not errorlevel 1 (
                        set "PY=%%~D\%%E\python.exe"
                        set "PY_OK=1"
                    )
                )
            )
        )
    )
)

:have_python
if "%PY_OK%"=="1" exit /b 0

echo.
echo  =====================================================
echo   Python was not found on this PC.
echo.
echo   1. Install it from:  https://www.python.org/downloads/
echo   2. IMPORTANT: tick "Add python.exe to PATH" on the
echo      first installer screen.
echo   3. After install, close this window and double-click
echo      this file again.
echo  =====================================================
echo.
exit /b 1
