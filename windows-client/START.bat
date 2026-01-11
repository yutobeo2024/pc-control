@echo off
cd /d "%~dp0"
echo Starting Parental Control Client...
start /min pythonw.exe main.py
timeout /t 2 /nobreak >nul
exit
