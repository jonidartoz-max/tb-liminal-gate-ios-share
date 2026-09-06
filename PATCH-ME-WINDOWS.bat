@echo off
title Terra Battle IPA Auto-Patcher
cd /d "%~dp0"
setlocal enableextensions

rem --- locate a working Python (prefers bundled portable runtime\) ---
call "%~dp0run_common.bat"
if errorlevel 1 (
    echo.
    echo Python not found. Install from python.org or keep runtime\ folder.
    echo.
    pause & exit /b 1
)

rem --- run the patcher; always pause so the window never vanishes ---
"%PY%" "%~dp0PATCH-ME.py"
echo.
pause
