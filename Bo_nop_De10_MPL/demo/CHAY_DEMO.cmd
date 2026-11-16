@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python demo.py --interactive
) else (
  py -3 demo.py --interactive
)
pause
