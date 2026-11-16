@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
where python >nul 2>&1
if not errorlevel 1 (
  python wenmo.py %*
) else (
  py -3 wenmo.py %*
)
if errorlevel 1 pause
