@echo off
REM Parental Control - Windows Client Launcher
REM Chạy app ẩn (không hiện console)

cd /d "%~dp0"
start "" pythonw.exe main.py
