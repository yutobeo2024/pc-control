@echo off
REM Parental Control - Debug Mode
REM Chạy app với console để xem log

chcp 65001 >nul
cd /d "%~dp0"
echo Starting Parental Control Client...
echo.
python.exe main.py
pause
